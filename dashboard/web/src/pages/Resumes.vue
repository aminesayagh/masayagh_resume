<script setup>
// Resumes ( /resumes ): every composition, with or without a job offer, with its score.
// Read: GET /api/resumes. "+ New resume" runs src/resumes.py new on the server (best candidate of each bloc, or a copy
// of another resume's choices); a row opens /resumes/<id>.
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

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

const status = (r) => (r.sent ? `Sent ${r.sent}` : r.approved ? `Approved ${r.approved}` : 'Draft')
const lines = (r) => (!r.lines ? 'Not recorded' : `${r.ready} / ${r.lines} Ready${r.scored < r.lines ? ` · ${r.lines - r.scored} not scored` : ''}`)
const cap = (t) => (t ? t[0].toUpperCase() + t.slice(1) : 'Not reviewed')

const dialog = reactive({ open: false, name: '', offer: null, start: 'best', from: null })
const busy = ref(false)
const canCreate = computed(() => dialog.name.trim() && (dialog.start === 'best' || dialog.from))
async function create() {
  busy.value = true
  try {
    const res = await fetch('/api/resumes', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: dialog.name.trim(), offer_id: dialog.offer, from_id: dialog.start === 'copy' ? dialog.from : null }),
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
  <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
  <div v-else-if="!data" class="muted">Loading…</div>
  <template v-else>
    <div class="head">
      <h1>Resumes · {{ data.resumes.length }}</h1>
      <el-button type="primary" @click="Object.assign(dialog, { open: true, name: '', offer: null, start: 'best', from: null })">
        + New resume</el-button>
    </div>
    <el-table :data="data.resumes" class="list" row-class-name="row" @row-click="(r) => router.push(`/resumes/${r.id}`)">
      <el-table-column prop="name" label="Name" min-width="260" sortable />
      <el-table-column label="Job offer" min-width="240" sortable :sort-by="(r) => r.offer || ''">
        <template #default="{ row }"><span :class="{ muted: !row.offer }">{{ row.offer || 'No offer' }}</span></template>
      </el-table-column>
      <el-table-column prop="created" label="Created" width="120" sortable />
      <el-table-column label="Status" width="160" sortable :sort-by="status">
        <template #default="{ row }">{{ status(row) }}</template>
      </el-table-column>
      <el-table-column label="Score" width="100" sortable :sort-by="(r) => r.score ?? -1">
        <template #default="{ row }"><b>{{ row.score != null ? `${row.score}%` : '—' }}</b></template>
      </el-table-column>
      <el-table-column label="Lines" min-width="190">
        <template #default="{ row }"><span class="muted">{{ lines(row) }}</span></template>
      </el-table-column>
      <el-table-column label="Summary" width="130">
        <template #default="{ row }"><span class="muted">{{ cap(row.summary) }}</span></template>
      </el-table-column>
    </el-table>
    <p class="muted small">Click a row to open that resume. Sent resumes open read-only. Score: the reviews of the line
      candidates each resume uses (reviewed lines only).</p>

    <el-dialog v-model="dialog.open" title="New resume" width="560px">
      <el-form label-position="top">
        <el-form-item label="Name">
          <el-input v-model="dialog.name" placeholder="e.g. AI engineer, short version" maxlength="120" />
        </el-form-item>
        <el-form-item label="Job offer (optional)">
          <el-select v-model="dialog.offer" clearable placeholder="No offer" style="width: 100%">
            <el-option v-for="o in data.offers" :key="o.id" :label="o.label" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Start from">
          <el-radio-group v-model="dialog.start" class="start">
            <el-radio value="best">The best candidate of each bloc</el-radio>
            <el-radio value="copy">A copy of another resume</el-radio>
          </el-radio-group>
          <el-select v-if="dialog.start === 'copy'" v-model="dialog.from" placeholder="Choose a resume" style="width: 100%; margin-top: 8px">
            <el-option v-for="r in data.resumes" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <p class="muted small">Creating builds the resume (a few seconds).</p>
      <template #footer>
        <el-button @click="dialog.open = false">Cancel</el-button>
        <el-button type="primary" :loading="busy" :disabled="!canCreate" @click="create">Create</el-button>
      </template>
    </el-dialog>
  </template>
</template>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.head h1 { font-size: 22px; margin: 0; }
.list :deep(.row) { cursor: pointer; }
.start { display: flex; flex-direction: column; align-items: flex-start; gap: 4px; }
.small { font-size: 12px; }
</style>
