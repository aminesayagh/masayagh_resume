<script setup>
// Requirements ( /requirements, was /skills ): every posting term across jobs, typed from the skills table.
// Posting terms are requirements, not skills. Read only: type, dates and keywords are not editable yet.
import { computed, onMounted, ref } from 'vue'

const data = ref(null)
const error = ref('')
onMounted(async () => {
  try {
    const res = await fetch('/api/requirements')
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    data.value = await res.json()
  } catch (e) {
    error.value = `Could not load the requirements: ${e.message}`
  }
})

const TYPE_LABEL = { technical: 'hard skill', design: 'hard skill · design', ai: 'hard skill · AI', soft: 'soft skill',
  language: 'language', location: 'location' }
const typeLabel = (t) => TYPE_LABEL[t.type] ?? 'not typed'
const TABS = {
  all: ['All', () => true],
  hard: ['Hard skills', (t) => t.hard],
  soft: ['Soft skills', (t) => t.type === 'soft'],
  language: ['Languages', (t) => t.type === 'language'],
  location: ['Location', (t) => t.type === 'location'],
  education: ['Education', () => false], // no education type in the db yet
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
      There is no education type in the database yet: degree terms such as “Computer Science” are still typed technical,
      so they appear under Hard skills.
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
            <el-select :model-value="typeLabel(selected)" disabled style="width: 200px" />
            <span class="muted hint">not wired yet</span>
          </el-form-item>
          <template v-if="selected.hard">
            <el-form-item label="Start">
              <el-input :model-value="selected.start ?? ''" placeholder="YYYY-MM" disabled style="width: 120px" />
              <span class="muted hint">End</span>
              <el-input :model-value="selected.end ?? ''" placeholder="still using" disabled style="width: 120px" />
            </el-form-item>
            <el-form-item>
              <el-tooltip content="Not wired yet"><span><el-button disabled>Save</el-button></span></el-tooltip>
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
          <el-tooltip content="Not wired yet"><span><el-button size="small" disabled>+ add</el-button></span></el-tooltip>
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
