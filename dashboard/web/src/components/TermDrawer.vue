<script setup>
// The term drawer (Requirements page and job page Skills tab): a term's type, dates (hard skills) and keywords, written
// through src/skills_inventory.py on the server, plus the jobs asking for it. Loads /api/requirements itself.
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { HARD, TYPE_LABEL } from '../skillTypes.js'

const props = defineProps({ term: { type: String, default: null } })  // lowercase posting term
const open = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['changed'])  // after a saved change: the parent reloads its own data

const selected = ref(null)
async function load() {
  const res = await fetch('/api/requirements')
  const t = props.term?.toLowerCase()
  const found = res.ok ? (await res.json()).terms.find((x) => x.term.toLowerCase() === t) : null
  // a term no requirement uses any more (old review.json): it can still be typed, which creates its skill
  selected.value = found ?? { term: t, type: null, hard: false, skill: null, keywords: [], jobs: 0, asked: [] }
}
watch(() => [open.value, props.term], () => { if (open.value && props.term) load() }, { immediate: true })

const form = ref({ type: null, start: '', end: '', keyword: '', lang: 'en', adding: false })
watch(selected, (t) => {
  form.value = { type: t?.type ?? null, start: t?.start ?? '', end: t?.end ?? '', keyword: '', lang: 'en', adding: false }
})
const MONTH = /^\d{4}(-(0[1-9]|1[0-2]))?$/
const startError = computed(() => (MONTH.test(form.value.start) ? '' : 'YYYY or YYYY-MM'))
const endError = computed(() => (!form.value.end || MONTH.test(form.value.end) ? '' : 'YYYY or YYYY-MM, or empty'))
const datesChanged = computed(() => form.value.start !== (selected.value?.start ?? '')
  || form.value.end !== (selected.value?.end ?? ''))
const busy = ref(false)
const query = ref('')

async function post(url, body, done, what) {
  busy.value = true
  try {
    const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
    const out = await res.json()
    const detail = Array.isArray(out.detail) ? out.detail.map((d) => d.msg).join('; ') : out.detail
    if (!res.ok || !out.ok) throw new Error(detail || out.output || `${res.status} ${res.statusText}`)
    const reviewed = out.reviewed?.length ? ` · review recomputed for ${out.reviewed.length} job${out.reviewed.length > 1 ? 's' : ''}` : ''
    ElMessage.success(done + reviewed)
    await load() // the drawer stays on the same term
    emit('changed', what)
  } catch (e) {
    ElMessage.error({ message: e.message, duration: 6000 })
  } finally {
    busy.value = false
  }
}
const saveType = (type) => post('/api/skills/type', { term: selected.value.skill ?? selected.value.term, type },
  `${selected.value.term}: ${TYPE_LABEL[type]}` + (HARD.includes(type) || !selected.value.start ? '' : ' (dates removed)'), 'type')
const saveDates = () => post('/api/skills/dates',
  { skill: selected.value.skill, start: form.value.start, end: form.value.end || null }, 'Dates saved', 'dates')
const addKeyword = () => post('/api/skills/keyword',
  { skill: selected.value.skill, keyword: form.value.keyword.trim(), lang: form.value.lang },
  `‘${form.value.keyword.trim()}’ now counts as ${selected.value.skill}`, 'keyword')
// Merge: move this term's keyword under another skill (its old skill is dropped once it has no keyword left)
const skills = ref([])
const target = ref('')
const others = computed(() => skills.value.filter((x) => x.name !== selected.value?.skill))
const keywordsOf = (x) => x.keywords.map((k) => k.keyword).filter((k) => k !== x.name).join(', ')
watch(open, async (o) => {
  if (!o) return
  target.value = ''
  const res = await fetch('/api/skills')
  if (res.ok) skills.value = (await res.json()).skills
}, { immediate: true })
const lastKeyword = computed(() => selected.value?.keywords.every((k) => k.keyword === selected.value.term))
async function moveTo() {
  const term = selected.value.term
  await post('/api/skills/move', { keyword: term, skill: target.value },
    `‘${term}’ now counts as ${target.value}` + (lastKeyword.value ? ` (${selected.value.skill} dropped)` : ''), 'move')
  target.value = ''
  skills.value = (await (await fetch('/api/skills')).json()).skills
}
const STATUS_TAG = { met: 'success', partial: 'warning', missing: 'danger' }
</script>

<template>
<el-drawer v-model="open" :title="selected?.term" size="40%">
  <template v-if="selected">
    <el-form label-width="70px" size="small">
      <el-form-item label="Type">
        <el-select v-model="form.type" placeholder="not typed" :disabled="busy" style="width: 200px"
          @change="saveType">
          <el-option v-for="(label, key) in TYPE_LABEL" :key="key" :label="label" :value="key" />
        </el-select>
        <span v-if="selected.skill && selected.skill.toLowerCase() !== selected.term.toLowerCase()" class="muted hint">
          via {{ selected.skill }}</span>
      </el-form-item>
      <template v-if="selected.hard">
        <el-form-item label="Start" :error="form.start && startError">
          <el-input v-model.trim="form.start" placeholder="YYYY-MM" :disabled="busy" style="width: 120px" />
        </el-form-item>
        <el-form-item label="End" :error="endError">
          <el-input v-model.trim="form.end" placeholder="still using" clearable :disabled="busy" style="width: 120px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="busy" :disabled="!datesChanged || !!startError || !!endError"
            @click="saveDates">Save</el-button>
        </el-form-item>
      </template>
      <p v-else class="muted small">Start / end dates are for hard skills only.</p>
    </el-form>

    <h4>Keywords <span class="muted small">(any one on the resume = has it)</span></h4>
    <div class="keywords">
      <span v-if="!selected.keywords.length" class="muted">{{ selected.type ? 'none' : 'no skills-table entry yet' }}</span>
      <el-tag v-for="k in selected.keywords" :key="k.keyword + k.lang" type="info">
        {{ k.keyword }}<span v-if="k.lang === 'fr'" class="muted"> · fr</span>
      </el-tag>
      <template v-if="form.adding">
        <el-input v-model="form.keyword" size="small" placeholder="true synonym only" maxlength="80"
          :disabled="busy" style="width: 170px" @keyup.enter="form.keyword.trim() && addKeyword()" />
        <el-select v-model="form.lang" size="small" :disabled="busy" style="width: 70px">
          <el-option label="en" value="en" /><el-option label="fr" value="fr" />
        </el-select>
        <el-button size="small" type="primary" :loading="busy" :disabled="!form.keyword.trim()"
          @click="addKeyword">Add</el-button>
        <el-button size="small" text :disabled="busy" @click="form.adding = false">Cancel</el-button>
      </template>
      <el-tooltip v-else :disabled="!!selected.skill" content="Give the term a type first">
        <span><el-button size="small" :disabled="!selected.skill" @click="form.adding = true">+ add</el-button></span>
      </el-tooltip>
    </div>

    <h4>Merge into another skill</h4>
<div class="merge">
  <el-select v-model="target" filterable clearable placeholder="Search a skill by name or keyword" :disabled="busy || !selected.skill"
    :filter-method="(q) => (query = q.toLowerCase())" style="width: 300px" @visible-change="(v) => v || (query = '')">
    <el-option v-for="x in others.filter((x) => !query || x.name.includes(query) || x.keywords.some((k) => k.keyword.includes(query)))"
      :key="x.name" :label="x.name" :value="x.name">
      <span>{{ x.name }}</span>
      <span class="muted opt">{{ TYPE_LABEL[x.type] ?? 'not typed' }}<template v-if="keywordsOf(x)"> · {{ keywordsOf(x) }}</template></span>
    </el-option>
  </el-select>
  <el-button type="primary" size="small" :loading="busy" :disabled="!target" @click="moveTo">Move ‘{{ selected.term }}’ here</el-button>
</div>
<p class="muted small">
  ‘{{ selected.term }}’ becomes a keyword of the chosen skill and takes its type.
  <template v-if="!selected.skill">Give the term a type first.</template>
  <template v-else-if="lastKeyword">{{ selected.skill }} has no other keyword: it will be dropped.</template>
  <template v-else>{{ selected.skill }} keeps its other keywords.</template>
</p>

<h4>Asked by {{ selected.jobs }} job{{ selected.jobs > 1 ? 's' : '' }} · status · wording</h4>
    <router-link v-for="a in selected.asked" :key="a.slug" class="asked"
      :to="{ path: `/job/${a.slug}/skills`, query: { term: selected.term } }">
      <div>
        <div><b>{{ a.company }}</b> · {{ a.role }} <span class="muted">({{ a.job_status }})</span></div>
        <div class="muted small">
          wording: {{ a.wording === 'exact' ? `exact ‘${selected.term}’` : a.wording === 'synonym' ? 'synonym' : 'not on the resume' }}
        </div>
      </div>
      <el-tag v-if="a.status" size="small" :type="STATUS_TAG[a.status]">{{ a.status }}</el-tag>
      <span v-else class="muted">—</span>
    </router-link>
    <p class="muted small">A job opens its page filtered on this term.</p>
  </template>
</el-drawer>
</template>

<style scoped>
.small { font-size: 12px; }
.hint { margin: 0 8px; }
.merge { display: flex; gap: 8px; align-items: center; }
.opt { float: right; margin-left: 16px; font-size: 12px; max-width: 220px; overflow: hidden; text-overflow: ellipsis; }
.keywords { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.asked { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #ebeef5;
  color: inherit; text-decoration: none; font-size: 14px; }
.asked:hover b { color: var(--el-color-primary); }
</style>
