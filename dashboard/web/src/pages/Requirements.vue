<script setup>
// Requirements ( /requirements, was /skills ): every posting term across jobs, typed from the skills table.
// Posting terms are requirements, not skills. The term drawer edits a term's type, dates (hard skills) and keywords
// through src/skills_inventory.py on the server.
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

const data = ref(null)
const error = ref('')
async function load() {
  try {
    const res = await fetch('/api/requirements')
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    data.value = await res.json()
  } catch (e) {
    error.value = `Could not load the requirements: ${e.message}`
  }
}
onMounted(load)

const TYPE_LABEL = { technical: 'hard skill', design: 'hard skill · design', ai: 'hard skill · AI', soft: 'soft skill',
  language: 'language', location: 'location', education: 'education' }
const HARD = ['technical', 'design', 'ai']
const typeLabel = (t) => TYPE_LABEL[t.type] ?? 'not typed'
const TABS = {
  all: ['All', () => true],
  hard: ['Hard skills', (t) => t.hard],
  soft: ['Soft skills', (t) => t.type === 'soft'],
  language: ['Languages', (t) => t.type === 'language'],
  location: ['Location', (t) => t.type === 'location'],
  education: ['Education', (t) => t.type === 'education'],
  untyped: ['Not typed yet', (t) => !t.type],
}
const tab = ref('all')
const q = ref('')
const twoPlus = ref(false)
const missingSomewhere = ref(false)
const synonym = ref(false)

const terms = computed(() => data.value?.terms ?? [])
const tabCount = (key) => terms.value.filter(TABS[key][1]).length
const shown = computed(() => {
  const needle = q.value.trim().toLowerCase()
  return terms.value.filter((t) => TABS[tab.value][1](t)
    && (!needle || t.term.toLowerCase().includes(needle) || t.keywords.some((k) => k.keyword.toLowerCase().includes(needle)))
    && (!twoPlus.value || t.jobs >= 2)
    && (!missingSomewhere.value || t.missing > 0)
    && (!synonym.value || t.synonym))
})
const cards = computed(() => ({
  total: terms.value.length,
  twoPlus: terms.value.filter((t) => t.jobs >= 2).length,
  missing: terms.value.filter((t) => t.missing > 0).length,
  untyped: terms.value.filter((t) => !t.type).length,
  synonym: terms.value.filter((t) => t.synonym).length,
}))
function card(key) {
  tab.value = key === 'untyped' ? 'untyped' : 'all'
  twoPlus.value = key === 'twoPlus'
  missingSomewhere.value = key === 'missing'
  synonym.value = false
}
const mostMissing = computed(() => terms.value.filter((t) => t.missing > 0)
  .sort((a, b) => b.missing - a.missing || a.term.localeCompare(b.term)).slice(0, 6))

const selected = ref(null)
const drawerOpen = ref(false)
function open(t) {
  selected.value = t
  drawerOpen.value = true
}

// Term drawer form
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

async function post(url, body, done) {
  busy.value = true
  try {
    const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
    const out = await res.json()
    const detail = Array.isArray(out.detail) ? out.detail.map((d) => d.msg).join('; ') : out.detail
    if (!res.ok || !out.ok) throw new Error(detail || out.output || `${res.status} ${res.statusText}`)
    ElMessage.success(done)
    const term = selected.value.term.toLowerCase()
    await load() // the page reloads its data; the drawer stays on the same term
    selected.value = data.value.terms.find((t) => t.term.toLowerCase() === term) ?? null
  } catch (e) {
    ElMessage.error({ message: e.message, duration: 6000 })
  } finally {
    busy.value = false
  }
}
const saveType = (type) => post('/api/skills/type', { term: selected.value.skill ?? selected.value.term, type },
  `${selected.value.term}: ${TYPE_LABEL[type]}` + (HARD.includes(type) || !selected.value.start ? '' : ' (dates removed)'))
const saveDates = () => post('/api/skills/dates',
  { skill: selected.value.skill, start: form.value.start, end: form.value.end || null }, 'Dates saved')
const addKeyword = () => post('/api/skills/keyword',
  { skill: selected.value.skill, keyword: form.value.keyword.trim(), lang: form.value.lang },
  `‘${form.value.keyword.trim()}’ now counts as ${selected.value.skill}`)
const STATUS_TAG = { met: 'success', partial: 'warning', missing: 'danger' }
const seg = (t, s) => `${(t[s] / t.jobs) * 100}%`
</script>

<template>
  <h1>Requirements</h1>
  <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
  <div v-else-if="!data" v-loading="true" style="height: 200px" />

  <template v-else>
    <el-row :gutter="16" class="cards">
      <el-col :span="6">
        <el-card shadow="hover" class="kpi" @click="card('all')">
          <div class="kpi-label">Requirement terms</div>
          <div class="kpi-value">{{ cards.total }}</div>
          <div class="muted">across {{ data.jobs }} jobs</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi" @click="card('twoPlus')">
          <div class="kpi-label">Asked by 2+ jobs</div>
          <div class="kpi-value">{{ cards.twoPlus }}</div>
          <div class="muted">the ones worth investing in</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi" @click="card('missing')">
          <div class="kpi-label">Missing somewhere</div>
          <div class="kpi-value">{{ cards.missing }}</div>
          <div class="muted">not on at least one resume</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi" @click="card('untyped')">
          <div class="kpi-label">Not typed yet</div>
          <div class="kpi-value">{{ cards.untyped }}</div>
          <div class="muted">no entry in the skills table</div>
        </el-card>
      </el-col>
    </el-row>

    <el-tabs v-model="tab">
      <el-tab-pane v-for="(t, key) in TABS" :key="key" :name="key" :label="`${t[0]}  ${tabCount(key)}`" />
    </el-tabs>
    <p v-if="tab === 'education'" class="muted small">
      Degrees and fields of study. Terms such as “Computer Science” may still be typed hard skill: open one and change
      its type to education.
    </p>

    <div class="filters">
      <el-input v-model="q" placeholder="Search a term or keyword" clearable style="width: 240px" />
      <el-check-tag :checked="twoPlus" @change="twoPlus = !twoPlus">2+ jobs</el-check-tag>
      <el-check-tag :checked="missingSomewhere" @change="missingSomewhere = !missingSomewhere">Missing somewhere</el-check-tag>
      <el-check-tag :checked="synonym" @change="synonym = !synonym">Synonym only {{ cards.synonym }}</el-check-tag>
    </div>

    <el-row :gutter="20">
      <el-col :span="17">
        <el-table :data="shown" size="small" empty-text="No term matches these filters" class="clickable"
          @row-click="open">
          <el-table-column prop="term" label="Term" min-width="170" />
          <el-table-column label="Type" width="150">
            <template #default="{ row }">
              <el-tag size="small" :type="row.type ? (row.hard ? 'primary' : 'success') : 'info'" round>{{ typeLabel(row) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="jobs" label="Jobs" width="60" />
          <el-table-column label="Met / partial / missing" min-width="190">
            <template #default="{ row }">
              <div class="stack" :title="`${row.met} met · ${row.partial} partial · ${row.missing} missing`">
                <span class="met" :style="{ width: seg(row, 'met') }" />
                <span class="partial" :style="{ width: seg(row, 'partial') }" />
                <span class="missing" :style="{ width: seg(row, 'missing') }" />
              </div>
              <span class="muted small">{{ row.met }}/{{ row.partial }}/{{ row.missing }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Your experience" width="150">
            <template #default="{ row }">
              <span :class="{ muted: !row.experience || row.experience === 'start date needed' }">{{ row.experience ?? '—' }}</span>
            </template>
          </el-table-column>
          <el-table-column width="40"><template #default>→</template></el-table-column>
        </el-table>
        <p class="muted small">{{ cards.total }} terms · showing {{ shown.length }} · sorted by jobs asking.
          Status per job: met if any keyword is on that resume.</p>
      </el-col>

      <el-col :span="7">
        <el-card shadow="never" class="block">
          <template #header>Most often missing</template>
          <div v-for="t in mostMissing" :key="t.term" class="side-row" @click="open(t)">
            <span class="link">{{ t.term }}</span><span class="muted">missing in {{ t.missing }} job{{ t.missing > 1 ? 's' : '' }}</span>
          </div>
        </el-card>
        <el-card shadow="never" class="block">
          <template #header>Start dates (hard skills only)</template>
          <p><b>{{ data.hard_with_start }} of {{ data.hard_entries }}</b> hard-skill entries have a start date.</p>
          <p class="muted small">Enter them in a term's drawer: start, and end if you stopped using it.
            Years are counted from these dates only.</p>
        </el-card>
      </el-col>
    </el-row>

    <el-drawer v-model="drawerOpen" :title="selected?.term" size="40%">
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

        <h4>Asked by {{ selected.jobs }} job{{ selected.jobs > 1 ? 's' : '' }} · status · wording</h4>
        <router-link v-for="a in selected.asked" :key="a.slug" class="asked"
          :to="{ path: `/job/${a.slug}`, query: { term: selected.term } }">
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
</template>

<style scoped>
.cards { margin-bottom: 8px; }
.kpi { cursor: pointer; }
.kpi-label { font-size: 13px; color: #606266; }
.kpi-value { font-size: 28px; font-weight: 600; margin: 4px 0; }
.filters { display: flex; gap: 10px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }
.small { font-size: 12px; }
.clickable :deep(tr) { cursor: pointer; }
.stack { display: inline-flex; width: 110px; height: 8px; border-radius: 4px; overflow: hidden; background: #ebeef5;
  vertical-align: middle; margin-right: 8px; }
.stack .met { background: #67c23a; }
.stack .partial { background: #e6a23c; }
.stack .missing { background: #f56c6c; }
.block { margin-bottom: 16px; }
.side-row { display: flex; justify-content: space-between; font-size: 14px; margin: 6px 0; cursor: pointer; }
.link { color: var(--el-color-primary); }
.hint { margin: 0 8px; }
.keywords { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.asked { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #ebeef5;
  color: inherit; text-decoration: none; font-size: 14px; }
.asked:hover b { color: var(--el-color-primary); }
</style>
