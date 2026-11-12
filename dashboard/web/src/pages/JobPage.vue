<script setup>
// Job page ( /job/<slug> ): header, links, last build, coverage, gaps, requirements, files, timeline, drawers.
// Write actions run src/ scripts on the server (Mark as sent, New version); the rest are shown disabled ("not wired yet").
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TermDrawer from '../components/TermDrawer.vue'
import InterviewPrep from './InterviewPrep.vue'
import { newVersion } from '../newVersion.js'
import { markSent } from '../markSent.js'

const route = useRoute()
const router = useRouter()
const job = ref(null)
const prep = ref(null)
const error = ref('')
const postingOpen = ref(false)
const docsOpen = ref(false)
const docTab = ref('resume')
const reqChip = ref('all')

async function load(refresh = false) {  // refresh: keep the page (and an open drawer) while the new data loads
  if (!refresh) {
    job.value = null
    prep.value = null
  }
  error.value = ''
  try {
    const base = `/api/jobs/${encodeURIComponent(route.params.slug)}`
    const [res, resPrep] = await Promise.all([fetch(base), fetch(`${base}/interview`)])
    if (!res.ok) throw new Error(res.status === 404 ? 'No such job' : `${res.status} ${res.statusText}`)
    job.value = await res.json()
    prep.value = resPrep.ok ? await resPrep.json() : { exists: false, topics: [] }
  } catch (e) {
    error.value = e.message
  }
}
watch(() => route.params.slug, () => load(), { immediate: true })

// Tabs are URLs: /job/<slug> (Overview), /job/<slug>/skills and /job/<slug>/interview.
const tab = computed({
  get: () => route.params.tab || 'overview',
  set: (v) => router.replace({ path: `/job/${route.params.slug}${v === 'overview' ? '' : `/${v}`}`, query: route.query }),
})

const pct = (v) => Math.round(v * 100)
const barColor = (v) => (v >= 0.75 ? '#67c23a' : '#e6a23c')
const PRIORITY = { must_have: 'must', preferred: 'pref' }
const STATUS_TAG = { met: 'success', partial: 'warning', missing: 'danger', uncertain: 'info' }
// Column sorts by rank, not alphabet: must before preferred; missing, partial, uncertain, then met
const priorityRank = (r) => (r.priority === 'must_have' ? 0 : 1)
const statusRank = (r) => ({ missing: 0, partial: 1, uncertain: 2, met: 3 })[r.status] ?? 4
const version = (slug) => slug.match(/-v(\d+)$/)?.[1] ?? '1'
const warnings = computed(() => job.value.notes.filter((n) => n.severity !== 'info'))
const infos = computed(() => job.value.notes.filter((n) => n.severity === 'info'))

const CHIPS = {
  all: ['All', () => true],
  met: ['Met', (r) => r.status === 'met'],
  partial: ['Partial', (r) => r.status === 'partial'],
  missing: ['Missing', (r) => r.status === 'missing'],
  uncertain: ['Uncertain', (r) => r.status === 'uncertain'],
  must: ['Must', (r) => r.priority === 'must_have'],
  preferred: ['Preferred', (r) => r.priority === 'preferred'],
}
// ?term=<t> (from the Requirements page): only the requirements using that term
const termFilter = computed(() => route.query.term?.toString().toLowerCase() || '')
const hasTerm = (r) => !termFilter.value || r.terms.some((t) => t.term.toLowerCase() === termFilter.value)
// Skills tab: search (requirement, terms, evidence) and type, on top of the chips and ?term=
const TYPE_LABEL = { technical: 'technical', design: 'design', ai: 'AI', soft: 'soft skill', language: 'language',
  location: 'location', education: 'education' }
const typeLabel = (r) => TYPE_LABEL[r.type] ?? 'not typed'
// Term drawer (same as the Requirements page): edit a requirement's skill without leaving the job
const drawerTerm = ref(null)
const termOpen = ref(false)
const editTerm = (term) => { drawerTerm.value = term.toLowerCase(); termOpen.value = true }
watch(() => route.fullPath, () => { termOpen.value = false })
// Skills tab: one card per status (all requirements, whatever the filters); a click filters the table
const STATES = {
  met: ['Met', 'on the resume'], partial: ['Partial', 'some of the terms'],
  missing: ['Missing', 'not on the resume'], uncertain: ['Uncertain', 'to check by hand'],
}
const stateCount = (s, must = false) => job.value.requirements
  .filter((r) => r.status === s && (!must || r.priority === 'must_have')).length
const reqQ = ref('')
const reqType = ref('')
const reqTypes = computed(() => [...new Set(job.value.requirements.map(typeLabel))].sort())
const matches = (r) => {
  const text = [r.description, r.evidence, ...r.terms.map((t) => t.term)].join(' ').toLowerCase()
  return hasTerm(r) && (!reqType.value || typeLabel(r) === reqType.value)
    && reqQ.value.toLowerCase().split(/\s+/).filter(Boolean).every((w) => text.includes(w))
}
const reqs = computed(() => job.value.requirements.filter((r) => CHIPS[reqChip.value][1](r) && matches(r)))
const chipCount = (key) => job.value.requirements.filter((r) => CHIPS[key][1](r) && matches(r)).length

// Posting text cut into plain / term segments; a term takes its best status across requirements.
const termStatus = computed(() => {
  const best = {}
  const order = { met: 3, partial: 2, uncertain: 1, missing: 0 }
  for (const r of job.value.requirements)
    for (const t of r.terms) {
      const k = t.term.toLowerCase()
      if (!(k in best) || order[t.status] > order[best[k]]) best[k] = t.status
    }
  return best
})
const segments = computed(() => {
  const text = job.value.posting
  const terms = Object.keys(termStatus.value).sort((a, b) => b.length - a.length)
  if (!terms.length) return [{ text }]
  const escaped = terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  const re = new RegExp(`(?<![\\p{L}\\p{N}])(${escaped.join('|')})(?![\\p{L}\\p{N}])`, 'giu')
  const out = []
  let last = 0
  for (const m of text.matchAll(re)) {
    if (m.index > last) out.push({ text: text.slice(last, m.index) })
    out.push({ text: m[0], status: termStatus.value[m[0].toLowerCase()] })
    last = m.index + m[0].length
  }
  out.push({ text: text.slice(last) })
  return out
})
const copied = ref(false)
async function copyPosting() {
  await navigator.clipboard.writeText(job.value.posting)
  copied.value = true
  setTimeout(() => (copied.value = false), 1500)
}

const fileOf = (lang, kind) => job.value.files[lang].find((f) => f.kind === kind)
const fileUrl = (f) => `/files/${job.value.slug}/${f.path}`
const KIND = { resume: 'Resume', cover: 'Cover letter', combined: 'Resume + cover letter' }
const docs = computed(() => ({
  resume: { label: 'Resume', file: fileOf('en', 'resume'), published: job.value.resume_url },
  cover: { label: 'Cover letter', file: fileOf('en', 'cover'), published: job.value.cover_letter_url },
  frResume: { label: 'French resume', file: fileOf('fr', 'resume'), published: null }, // French is never published
  frCover: { label: 'French letter', file: fileOf('fr', 'cover'), published: null },
}))
// French tabs only when there is (or should be) a French version
const docTabs = computed(() => Object.keys(docs.value)
  .filter((k) => !k.startsWith('fr') || job.value.files.fr.length || job.value.french_version))
function openDoc(tab) {
  docTab.value = tab
  docsOpen.value = true
}
const timeline = computed(() => job.value.timeline.filter((t) => t.date))
</script>

<template>
  <el-alert v-if="error" :title="error" type="error" show-icon :closable="false">
    <router-link to="/">← All jobs</router-link>
  </el-alert>
  <div v-else-if="!job" v-loading="true" style="height: 200px" />

  <template v-else>
    <router-link to="/" class="back">← All jobs</router-link>
    <div class="head">
      <div>
        <h1>{{ job.company }} · {{ job.role }}</h1>
        <div class="meta">
          <el-tag :type="job.status === 'sent' ? 'success' : 'primary'" round>{{ job.status }}</el-tag>
          <el-tag type="info" round>v{{ job.version }}</el-tag>
          <span>{{ job.location || 'location —' }}</span> ·
          <span>added {{ job.created }}</span> ·
          <span>versions:
            <template v-for="(v, i) in job.versions" :key="v">
              <span v-if="i">, </span>
              <b v-if="v === job.slug">v{{ version(v) }} (this one)</b>
              <router-link v-else :to="`/job/${v}`">v{{ version(v) }}</router-link>
            </template>
          </span>
          <span v-if="job.sent"> · sent {{ job.sent }} (frozen)</span>
        </div>
      </div>
      <div class="head-actions">
        <el-button v-if="!job.sent" type="primary" @click="markSent(job, load)">Mark as sent</el-button>
        <el-dropdown trigger="click">
          <el-button aria-label="More actions">⋯</el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="newVersion(job, router)">New version</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <el-tabs v-model="tab" class="page-tabs">
    <el-tab-pane label="Overview" name="overview">
    <el-row :gutter="20">
      <el-col :span="17">
        <el-card shadow="never" class="block">
          <template #header>
            Last build · {{ job.build.date || '—' }} · {{ warnings.length }} warning{{ warnings.length === 1 ? '' : 's' }},
            {{ infos.length }} info
          </template>
          <div v-if="!job.notes.length" class="muted">Nothing to report.</div>
          <div v-for="(n, i) in job.notes" :key="i" class="note">
            <el-tag size="small" :type="n.severity === 'info' ? 'info' : 'warning'">{{ n.severity === 'info' ? 'i' : '!' }}</el-tag>
            <span class="note-text">{{ n.text }}</span>
          </div>
        </el-card>

        <el-card shadow="never" class="block">
          <template #header>Evidence coverage</template>
          <div v-if="!job.has_requirements" class="muted">No requirements yet.</div>
          <div v-for="p in ['overall', 'must_have', 'preferred']" v-else :key="p" class="cov">
            <span class="cov-label">{{ { overall: 'Overall', must_have: 'Must-have', preferred: 'Preferred' }[p] }}</span>
            <template v-if="job.coverage[p].ratio != null">
              <el-progress :percentage="pct(job.coverage[p].ratio)" :color="barColor(job.coverage[p].ratio)"
                :stroke-width="10" class="cov-bar" />
              <span class="muted">met {{ job.coverage[p].met }} · partial {{ job.coverage[p].partial }}
                · missing {{ job.coverage[p].missing }}</span>
            </template>
            <span v-else class="muted">—</span>
          </div>
          <div class="muted small">Partial counts ½. Overall: a preferred skill counts ¼ of a must-have. A tailoring aid, not an ATS score.</div>
        </el-card>

        <el-card v-if="job.gaps.length" shadow="never" class="block">
          <template #header>Gaps to work on (must-have first) · {{ job.gaps.length }}</template>
          <el-table :data="job.gaps" max-height="420" size="small">
            <el-table-column prop="description" label="Requirement" min-width="200" />
            <el-table-column label="Priority" width="95" sortable :sort-by="priorityRank">
              <template #default="{ row }">{{ PRIORITY[row.priority] }}</template>
            </el-table-column>
            <el-table-column label="Status" width="100" sortable :sort-by="statusRank">
              <template #default="{ row }"><el-tag size="small" :type="STATUS_TAG[row.status]">{{ row.status }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="hint" label="Hint" min-width="260" />
            <el-table-column width="130">
              <template #default>
                <el-tooltip content="Not wired yet: how it works is decided later">
                  <span><el-button size="small" plain disabled class="dashed">Propose swap</el-button></span>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="7">
        <el-card shadow="never" class="block">
          <template #header>Files</template>
          <div class="links">
            <el-button link type="primary" @click="postingOpen = true">View posting</el-button>
            <a v-if="job.url" :href="job.url" target="_blank" rel="noopener">Original offer →</a>
            <a v-if="job.resume_url" :href="job.resume_url" target="_blank" rel="noopener">Published resume →</a>
            <a v-if="job.cover_letter_url" :href="job.cover_letter_url" target="_blank" rel="noopener">Published cover letter →</a>
          </div>
          <div class="lang">English</div>
          <div v-if="!job.files.en.length" class="muted">Not built yet</div>
          <div v-for="f in job.files.en" :key="f.path" class="file">
            <a :href="fileUrl(f)" target="_blank" rel="noopener">{{ KIND[f.kind] }}</a>
            <el-tag v-if="f.not_ready" size="small" type="warning">not ready</el-tag>
            <el-tag v-if="f.kind === 'resume' && f.pages > 3" size="small" type="warning">over 3 pages</el-tag>
          </div>
          <div class="preview-buttons">
            <el-button size="small" :disabled="!docs.resume.file" @click="openDoc('resume')">Preview resume</el-button>
            <el-button size="small" :disabled="!docs.cover.file" @click="openDoc('cover')">Preview letter</el-button>
          </div>
          <div class="lang">French</div>
          <div v-if="!job.files.fr.length" class="muted">
            {{ job.french_version ? 'Not built yet' : 'Not needed (English posting)' }}
          </div>
          <div v-for="f in job.files.fr" :key="f.path" class="file">
            <a :href="fileUrl(f)" target="_blank" rel="noopener">{{ KIND[f.kind] }}</a>
            <el-tag v-if="f.not_ready" size="small" type="warning">not ready</el-tag>
          </div>
          <div v-if="job.files.fr.length" class="preview-buttons">
            <el-button size="small" :disabled="!docs.frResume.file" @click="openDoc('frResume')">Preview resume</el-button>
            <el-button size="small" :disabled="!docs.frCover.file" @click="openDoc('frCover')">Preview letter</el-button>
          </div>
        </el-card>

        <el-card shadow="never" class="block">
          <template #header>Timeline</template>
          <el-timeline>
            <el-timeline-item v-for="t in timeline" :key="t.event" :timestamp="t.date">{{ t.event }}</el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
    </el-tab-pane>
    <el-tab-pane :label="`Skills (${job.requirements.length})`" name="skills">
        <el-row :gutter="16" class="state-cards">
          <el-col v-for="(c, key) in STATES" :key="key" :span="6">
            <el-card shadow="hover" :class="['state', `state-${key}`, { on: reqChip === key }]"
              @click="reqChip = reqChip === key ? 'all' : key">
              <div class="state-label">{{ c[0] }}</div>
              <div class="state-value">{{ stateCount(key) }}</div>
              <div class="muted small">{{ stateCount(key, true) }} must-have · {{ c[1] }}</div>
            </el-card>
          </el-col>
        </el-row>
        <el-card shadow="never" class="block">
          <div class="chips">
            <el-input v-model="reqQ" placeholder="Search requirement, term, evidence" clearable style="width: 260px" />
            <el-select v-model="reqType" placeholder="Type" clearable style="width: 150px">
              <el-option v-for="t in reqTypes" :key="t" :label="t" :value="t" />
            </el-select>
            <el-check-tag v-for="(c, key) in CHIPS" :key="key" :checked="reqChip === key" @change="reqChip = key">
              {{ c[0] }} {{ chipCount(key) }}
            </el-check-tag>
            <el-tag v-if="termFilter" closable type="primary" @close="router.replace({ query: {} })">
              term: {{ route.query.term }}
            </el-tag>
          </div>
          <el-table :data="reqs" row-key="id" size="small" empty-text="No requirement here">
            <el-table-column type="expand">
              <template #default="{ row }">
                <div class="expand">
                  <p><b>Posting:</b> {{ row.posting_quote || '—' }}</p>
                  <p><b>Terms:</b>
                    <span v-if="!row.terms.length" class="muted">—</span>
                    <el-tag v-for="t in row.terms" :key="t.term" size="small" :type="STATUS_TAG[t.status]" class="term">
                      {{ t.term }}<span v-if="t.keyword === 'alias'"> · synonym</span>
                    </el-tag>
                  </p>
                  <p><b>Override:</b>
                    <span v-if="row.override">{{ row.override.status }} — {{ row.override.reason }}</span>
                    <span v-else class="muted">none</span>
                  </p>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Requirement" min-width="220" sortable
              :sort-by="(r) => r.description.toLowerCase()" />
            <el-table-column label="Type" width="120" sortable :sort-by="typeLabel">
              <template #default="{ row }">
                <span :class="{ muted: !row.type }">{{ typeLabel(row) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Priority" width="95" sortable :sort-by="priorityRank">
              <template #default="{ row }">{{ PRIORITY[row.priority] }}</template>
            </el-table-column>
            <el-table-column label="Status" width="100" sortable :sort-by="statusRank">
              <template #default="{ row }"><el-tag size="small" :type="STATUS_TAG[row.status]">{{ row.status }}</el-tag></template>
            </el-table-column>
            <el-table-column label="Evidence (resume quote)" min-width="260">
              <template #default="{ row }">
                <span v-if="row.evidence">‘{{ row.evidence }}’</span><span v-else class="muted">—</span>
              </template>
            </el-table-column>
            <el-table-column width="56" align="center">
              <template #default="{ row }">
                <el-dropdown v-if="row.terms.length" trigger="click">
                  <el-button text size="small" aria-label="Actions">⋯</el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item v-for="t in row.terms" :key="t.term" @click="editTerm(t.term)">
                        Edit skill{{ row.terms.length > 1 ? `: ${t.term.toLowerCase()}` : '' }}
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
    </el-tab-pane>
    <el-tab-pane :label="`Interview prep (${prep?.topics.length ?? 0})`" name="interview">
      <InterviewPrep v-if="prep" :prep="prep" :job="job" @open-doc="openDoc" @open-posting="postingOpen = true" />
    </el-tab-pane>
    </el-tabs>

    <TermDrawer v-model="termOpen" :term="drawerTerm" @changed="load(true)" />

    <el-drawer v-model="postingOpen" :title="`Job posting · ${job.company}`" size="45%">
      <div class="drawer-actions">
        <a v-if="job.url" :href="job.url" target="_blank" rel="noopener">Original offer →</a>
        <el-button size="small" @click="copyPosting">{{ copied ? 'Copied' : 'Copy' }}</el-button>
      </div>
      <div class="muted small">Terms: <span class="t-met">green = met</span>, <span class="t-partial">yellow = partial</span>,
        <span class="t-missing">red = missing</span>. Saved text, so it stays readable even if the offer goes offline.</div>
      <div class="posting">
        <template v-for="(s, i) in segments" :key="i">
          <mark v-if="s.status" :class="`t-${s.status}`">{{ s.text }}</mark><template v-else>{{ s.text }}</template>
        </template>
      </div>
    </el-drawer>

    <el-drawer v-model="docsOpen" title="Documents" size="55%">
      <el-tabs v-model="docTab">
        <el-tab-pane v-for="key in docTabs" :key="key" :label="docs[key].label" :name="key">
          <template v-if="docs[key].file">
            <div class="drawer-actions">
              <a :href="fileUrl(docs[key].file)" :download="docs[key].file.name">Download</a>
              <a v-if="docs[key].published" :href="docs[key].published" target="_blank" rel="noopener">Published →</a>
            </div>
            <iframe v-if="docsOpen && docTab === key" :src="fileUrl(docs[key].file)" class="pdf" :title="docs[key].label" />
          </template>
          <div v-else class="muted">
            Not built yet.
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-drawer>
  </template>
</template>

<style scoped>
.back { color: #606266; text-decoration: none; font-size: 14px; }
.head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }
.head h1 { margin: 8px 0; }
.page-tabs { margin-top: 16px; }
.meta { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; color: #606266; font-size: 14px; }
.head-actions { display: flex; gap: 8px; margin-top: 12px; }
.links { display: flex; flex-direction: column; align-items: flex-start; gap: 6px; margin-bottom: 12px; font-size: 14px; }
.links .el-button { padding: 0; height: auto; font-size: 14px; }
.links a, .drawer-actions a, .file a { color: var(--el-color-primary); text-decoration: none; }
.block { margin-bottom: 16px; }
.note { display: flex; gap: 8px; align-items: baseline; margin: 6px 0; font-size: 14px; }
.note-text { flex: 1; }
.small { font-size: 12px; margin-top: 8px; }
.cov { display: flex; gap: 12px; align-items: center; margin: 8px 0; font-size: 14px; }
.cov-label { width: 80px; }
.cov-bar { width: 220px; }
.state-cards { margin-bottom: 16px; }
.state { cursor: pointer; border-top: 3px solid var(--state); }
.state.on { outline: 2px solid var(--state); }
.state-met { --state: #67c23a; }
.state-partial { --state: #e6a23c; }
.state-missing { --state: #f56c6c; }
.state-uncertain { --state: #909399; }
.state-label { font-size: 13px; color: #606266; }
.state-value { font-size: 28px; font-weight: 600; margin: 4px 0; }
.chips { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 8px; }
.expand { padding: 4px 48px; font-size: 13px; }
.term { margin: 2px 4px 2px 0; }
.dashed { border-style: dashed; }
.lang { font-weight: 600; margin: 8px 0 4px; font-size: 14px; }
.file { font-size: 14px; margin: 4px 0; display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.preview-buttons { margin: 8px 0 12px; }
.drawer-actions { display: flex; gap: 16px; align-items: center; margin-bottom: 8px; }
.posting { white-space: pre-wrap; line-height: 1.6; font-size: 14px; margin-top: 12px; }
mark { padding: 0 2px; border-radius: 3px; }
.t-met { background: #e1f3d8; color: #3b7a1f; }
.t-partial { background: #faecd8; color: #9a6411; }
.t-missing { background: #fde2e2; color: #c03636; }
.pdf { width: 100%; height: calc(100vh - 180px); border: 1px solid #e4e7ed; }
</style>
