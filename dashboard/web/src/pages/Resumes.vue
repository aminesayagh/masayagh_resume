<script setup>
// Resumes ( /resumes ): your own resumes, not written for a job offer (compositions with no offer_id), to work on
// their writing before tailoring one to an offer on the Jobs page. Read: GET /api/resumes. "+ New resume" runs
// src/resumes.py new on the server (the best candidate of each bloc, or a copy of another resume); a row opens it.
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const data = ref(null)
const error = ref('')
async function load() {
  try {
    const res = await fetch('/api/resumes')
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    data.value = await res.json()
  } catch (e) {
    error.value = `Could not load the resumes: ${e.message}`
  }
}
onMounted(load)

const rows = computed(() => data.value?.resumes ?? [])
const avg = (xs) => (xs.length ? Math.round(xs.reduce((a, b) => a + b, 0) / xs.length) : null)
const cards = computed(() => ({
  count: rows.value.length,
  score: avg(rows.value.filter((r) => r.score != null).map((r) => r.score)),
  ready: rows.value.reduce((a, r) => a + r.ready, 0),
  lines: rows.value.reduce((a, r) => a + r.lines, 0),
  summaries: rows.value.filter((r) => r.summary === 'ready').length,
}))
const q = ref('')
const chip = ref('all')
const CHIPS = { all: ['All', () => true], revise: ['Lines to revise', (r) => r.ready < r.lines], unscored: ['Not scored', (r) => r.scored < r.lines] }
const chipCount = (k) => rows.value.filter(CHIPS[k][1]).length
const shown = computed(() => rows.value.filter((r) => CHIPS[chip.value][1](r) && r.name.toLowerCase().includes(q.value.toLowerCase())))
const lines = (r) => (!r.lines ? 'Not recorded' : `${r.ready} / ${r.lines} Ready${r.scored < r.lines ? ` · ${r.lines - r.scored} not scored` : ''}`)
const cap = (t) => (t ? t[0].toUpperCase() + t.slice(1) : 'Not reviewed')

async function remove(row) {
  try {
    await ElMessageBox.confirm(`Delete “${row.name}”? Its folder and PDF go; the versions it used stay as candidates.`,
      'Delete resume', { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' })
  } catch { return }
  try {
    const res = await fetch(`/api/resumes/${row.id}/delete`, { method: 'POST' })
    const out = await res.json()
    if (!res.ok || !out.ok) throw new Error(out.detail || out.output || res.statusText)
    ElMessage.success('Deleted')
    await load()
  } catch (e) {
    ElMessage({ type: 'error', message: e.message, duration: 8000, showClose: true })
  }
}
const dialog = reactive({ open: false, start: 'best', from: null })
const busy = ref(false)
async function create() {
  busy.value = true
  try {
    const res = await fetch('/api/resumes', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ from_id: dialog.start === 'copy' ? dialog.from : null }),
    })
    const out = await res.json()
    if (!res.ok || !out.ok) throw new Error(out.detail || out.output || res.statusText)
    dialog.open = false
    router.push(`/resumes/${out.id}`)
  } catch (e) {
    ElMessage({ type: 'error', message: e.message, duration: 8000, showClose: true })
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <h1>Resumes</h1>
  <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
  <div v-else-if="!data" v-loading="true" style="height: 200px" />

  <template v-else>
    <el-row :gutter="16" class="cards">
      <el-col :span="6">
        <el-card shadow="hover" class="kpi" @click="chip = 'all'">
          <div class="kpi-label">Resumes</div>
          <div class="kpi-value">{{ cards.count }}</div>
          <div class="muted">not written for a job offer</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi" @click="chip = 'all'">
          <div class="kpi-label">Average score</div>
          <div class="kpi-value">{{ cards.score == null ? '—' : `${cards.score}%` }}</div>
          <div class="muted">of the reviewed lines</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi" @click="chip = 'revise'">
          <div class="kpi-label">Lines Ready</div>
          <div class="kpi-value">{{ cards.ready }} / {{ cards.lines }}</div>
          <div class="muted">across these resumes</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi" @click="chip = 'all'">
          <div class="kpi-label">Summaries Ready</div>
          <div class="kpi-value">{{ cards.summaries }} / {{ cards.count }}</div>
          <div class="muted">Name, Fame, Aim</div>
        </el-card>
      </el-col>
    </el-row>

    <div class="filters">
      <el-input v-model="q" placeholder="Search a resume" clearable style="width: 260px" />
      <el-check-tag v-for="(c, key) in CHIPS" :key="key" :checked="chip === key" @change="chip = key">
        {{ c[0] }} {{ chipCount(key) }}
      </el-check-tag>
      <span class="grow" />
      <el-button type="primary" @click="Object.assign(dialog, { open: true, start: 'best', from: null })">+ New resume</el-button>
    </div>

    <el-table :data="shown" row-class-name="row" @row-click="(r) => router.push(`/resumes/${r.id}`)">
      <template #empty>No resume yet: “+ New resume” starts one from the best candidate of each bloc.</template>
      <el-table-column prop="name" label="Name" min-width="240" sortable />
      <el-table-column prop="created" label="Created" width="130" sortable />
      <el-table-column label="Score" width="110" sortable :sort-by="(r) => r.score ?? -1">
        <template #default="{ row }"><b>{{ row.score != null ? `${row.score}%` : '—' }}</b></template>
      </el-table-column>
      <el-table-column label="Lines" min-width="200">
        <template #default="{ row }"><span class="muted">{{ lines(row) }}</span></template>
      </el-table-column>
      <el-table-column label="Summary" width="140">
        <template #default="{ row }"><span class="muted">{{ cap(row.summary) }}</span></template>
      </el-table-column>
      <el-table-column width="60" align="right">
        <template #default="{ row }">
          <span @click.stop>
            <el-dropdown trigger="click">
              <el-button text size="small" aria-label="Actions">⋯</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="remove(row)">Delete</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </span>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog.open" title="New resume" width="520px">
      <el-radio-group v-model="dialog.start" class="start">
        <el-radio value="best">The best candidate of each bloc</el-radio>
        <el-radio value="copy" :disabled="!rows.length">A copy of another resume</el-radio>
      </el-radio-group>
      <el-select v-if="dialog.start === 'copy'" v-model="dialog.from" placeholder="Choose a resume" style="width: 100%; margin-top: 8px">
        <el-option v-for="r in rows" :key="r.id" :label="r.name" :value="r.id" />
      </el-select>
      <template #footer>
        <el-button @click="dialog.open = false">Cancel</el-button>
        <el-button type="primary" :loading="busy" :disabled="dialog.start === 'copy' && !dialog.from" @click="create">Create</el-button>
      </template>
    </el-dialog>
  </template>
</template>

<style scoped>
.cards { margin-bottom: 20px; }
.kpi { cursor: pointer; }
.kpi-label { font-size: 13px; color: #606266; }
.kpi-value { font-size: 28px; font-weight: 600; margin: 4px 0; }
.filters { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 12px; }
.grow { flex: 1; }
:deep(.row) { cursor: pointer; }
.start { display: flex; flex-direction: column; align-items: flex-start; gap: 4px; }
</style>
