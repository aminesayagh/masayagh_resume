<script setup>
// Jobs list ( / ): summary cards, search + chips + filters, and the jobs table.
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { newVersion } from '../newVersion.js'
import { markSent } from '../markSent.js'

const router = useRouter()

const jobs = ref([])
const cards = ref({})
const loading = ref(true)
const error = ref('')
const q = ref('')
const chip = ref('all')
const skill = ref('')
const location = ref('')

async function load() {
  try {
    const res = await fetch('/api/jobs')
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    const body = await res.json()
    jobs.value = body.jobs
    cards.value = body.cards
  } catch (e) {
    error.value = `Could not load the jobs: ${e.message}`
  } finally {
    loading.value = false
  }
}
onMounted(load)

const CHIPS = {
  all: ['All', () => true],
  progress: ['In progress', (j) => j.status === 'in progress'],
  warnings: ['With warnings', (j) => j.warnings > 0],
  sent: ['Sent', (j) => j.status === 'sent'],
}
const chipCount = (key) => jobs.value.filter(CHIPS[key][1]).length
const skills = computed(() => [...new Set(jobs.value.flatMap((j) => j.terms))].sort((a, b) => a.localeCompare(b)))
const locations = computed(() => [...new Set(jobs.value.map((j) => j.location).filter(Boolean))].sort())

const shown = computed(() => {
  const words = q.value.toLowerCase().split(/\s+/).filter(Boolean)
  return jobs.value.filter((j) => {
    const text = [j.company, j.role, ...j.terms].join(' ').toLowerCase()
    return CHIPS[chip.value][1](j)
      && words.every((w) => text.includes(w))
      && (!skill.value || j.terms.includes(skill.value))
      && (!location.value || j.location === location.value)
  })
})

const pct = (v) => Math.round(v * 100)
const barColor = (v) => (v >= 0.75 ? '#67c23a' : '#e6a23c') // green >= 75%, yellow below
const rowClass = ({ row }) => (row.status === 'sent' ? 'frozen' : '')
const infoCount = (j) => j.notes.length - j.warnings
const todoLine = (j) => {
  if (!j.notes.length) return 'No warnings'
  const parts = []
  if (j.warnings) parts.push(`${j.warnings} warning${j.warnings > 1 ? 's' : ''}`)
  if (infoCount(j)) parts.push(`${infoCount(j)} info`)
  return parts.join(', ')
}
</script>

<template>
  <h1>Jobs</h1>
  <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />

  <el-row :gutter="16" class="cards">
    <el-col :span="6">
      <el-card shadow="hover" class="kpi" @click="chip = 'progress'">
        <div class="kpi-label">In progress</div>
        <div class="kpi-value">{{ cards.in_progress ?? '—' }}</div>
        <div class="muted">no sent date yet</div>
      </el-card>
    </el-col>
    <el-col :span="6">
      <el-card shadow="hover" class="kpi" @click="chip = 'warnings'">
        <div class="kpi-label">With warnings</div>
        <div class="kpi-value">{{ cards.with_warnings ?? '—' }}</div>
        <div class="muted">in progress, with warnings</div>
      </el-card>
    </el-col>
    <el-col :span="6">
      <el-card shadow="hover" class="kpi" @click="chip = 'sent'">
        <div class="kpi-label">Sent (30 days)</div>
        <div class="kpi-value">{{ cards.sent_30_days ?? '—' }}</div>
        <div class="muted">by sent date</div>
      </el-card>
    </el-col>
    <el-col :span="6">
      <el-card shadow="hover" class="kpi" @click="chip = 'progress'">
        <div class="kpi-label">Avg must-have coverage</div>
        <div class="kpi-value">{{ cards.avg_must_have == null ? '—' : pct(cards.avg_must_have) + '%' }}</div>
        <div class="muted">{{ cards.avg_must_have == null ? 'no open job with requirements' : 'across open jobs' }}</div>
      </el-card>
    </el-col>
  </el-row>

  <div class="filters">
    <el-input v-model="q" placeholder="Search company, role, skill" clearable style="width: 260px" />
    <el-check-tag v-for="(c, key) in CHIPS" :key="key" :checked="chip === key" @change="chip = key">
      {{ c[0] }} {{ chipCount(key) }}
    </el-check-tag>
    <el-select v-model="skill" placeholder="Skill" clearable filterable style="width: 180px">
      <el-option v-for="s in skills" :key="s" :label="s" :value="s" />
    </el-select>
    <el-select v-model="location" placeholder="Location" clearable style="width: 200px">
      <el-option v-for="l in locations" :key="l" :label="l" :value="l" />
    </el-select>
  </div>

  <el-table v-loading="loading" :data="shown" :row-class-name="rowClass"
    empty-text="No job matches these filters">
    <el-table-column label="Company / role" min-width="240" sortable :sort-by="(row) => `${row.company}\u0000${row.role}`.toLowerCase()">
      <template #default="{ row }">
        <router-link :to="`/job/${row.slug}`" class="company">{{ row.company }}</router-link>
        <div class="muted">{{ row.role }} · v{{ row.version }}<span v-if="row.versions > 1"> (latest of {{ row.versions }})</span><span v-if="row.sent">  (frozen)</span></div>
      </template>
    </el-table-column>
    <el-table-column label="Status" width="120" sortable sort-by="status">
      <template #default="{ row }">
        <el-tag :type="row.status === 'sent' ? 'success' : 'primary'" round>{{ row.status }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column v-for="p in ['overall', 'must_have', 'preferred']" :key="p"
      :label="{ overall: 'Overall', must_have: 'Must-have', preferred: 'Preferred' }[p]" width="150" sortable :sort-by="(row) => row[p] ?? -1">
      <template #default="{ row }">
        <span v-if="!row.has_requirements" class="muted">no requirements yet</span>
        <span v-else-if="row[p] == null" class="muted">—</span>
        <el-progress v-else :percentage="pct(row[p])" :color="barColor(row[p])" :stroke-width="8" />
      </template>
    </el-table-column>
    <el-table-column label="To do / info" min-width="200">
      <template #default="{ row }">
        <el-popover v-if="row.notes.length" trigger="hover" :width="420" placement="left">
          <template #reference><span class="todo">{{ todoLine(row) }}</span></template>
          <div v-for="(n, i) in row.notes" :key="i" class="note">
            <el-tag size="small" :type="n.severity === 'info' ? 'info' : 'warning'">{{ n.severity }}</el-tag>
            {{ n.text }}
          </div>
        </el-popover>
        <span v-else class="muted">No warnings</span>
      </template>
    </el-table-column>
    <el-table-column width="64" align="center">
      <template #default="{ row }">
        <el-dropdown trigger="click">
          <el-button text size="small" aria-label="Actions">⋯</el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-if="row.sent" disabled>Sent on {{ row.sent }}</el-dropdown-item>
              <el-dropdown-item v-else @click="markSent(row, load)">Mark as sent</el-dropdown-item>
              <el-dropdown-item @click="newVersion(row, router)">New version</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
    </el-table-column>
  </el-table>


  <p class="muted">{{ jobs.length }} offers, latest version of each · showing {{ shown.length }} · newest first.
    Partial counts ½. Overall: a preferred skill counts ¼ of a must-have. A tailoring aid, not an ATS score.</p>
</template>

<style scoped>
.cards { margin-bottom: 20px; }
.kpi { cursor: pointer; }
.kpi-label { font-size: 13px; color: #606266; }
.kpi-value { font-size: 28px; font-weight: 600; margin: 4px 0; }
.filters { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 12px; }
.company { font-weight: 600; color: inherit; text-decoration: none; }
a.company:hover { color: var(--el-color-primary); }
.todo { cursor: help; border-bottom: 1px dotted #909399; }
.note { margin: 6px 0; font-size: 13px; }
:deep(.el-table tr.frozen td) { color: #a8abb2; background: #fafafa; }
:deep(.el-table tr.frozen .company) { color: #909399; }
</style>
