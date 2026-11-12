<script setup>
// Job page ( /job/<slug> ): header, links, last build, coverage, gaps, requirements, files, timeline, drawers.
// Write actions run src/ scripts on the server (Mark as sent, New version); the rest are shown disabled ("not wired yet").
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
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

async function load() {
  job.value = null
  prep.value = null
  error.value = ''
  try {
    const base = `/api/jobs/${encodeURIComponent(route.params.slug)}`
    const [res, resPrep] = await Promise.all([fetch(base), fetch(`${base}/interview`)])
    if (!res.ok) throw new Error(res.status === 404 ? 'No such job' : `${res.status} ${res.statusText}`)
    job.value = await res.json()
    prep.value = resPrep.ok ? await resPrep.json() : { exists: false, topics: [] }
    if (route.query.term) {  // arriving from the Requirements page: show the filtered table
      await nextTick()
      document.getElementById('all-requirements')?.scrollIntoView({ behavior: 'smooth' })
    }
  } catch (e) {
    error.value = e.message
  }
}
watch(() => route.params.slug, load, { immediate: true })

// Tabs are URLs: /job/<slug> (Overview) and /job/<slug>/interview.
const tab = computed({
  get: () => (route.path.endsWith('/interview') ? 'interview' : 'overview'),
  set: (v) => router.replace({ path: `/job/${route.params.slug}${v === 'interview' ? '/interview' : ''}`, query: route.query }),
})

const pct = (v) => Math.round(v * 100)
const barColor = (v) => (v >= 0.75 ? '#67c23a' : '#e6a23c')
const PRIORITY = { must_have: 'must', preferred: 'pref' }
const STATUS_TAG = { met: 'success', partial: 'warning', missing: 'danger', uncertain: 'info' }
const version = (slug) => slug.match(/-v(\d+)$/)?.[1] ?? '1'
const warnings = computed(() => job.value.notes.filter((n) => n.severity !== 'info'))
const infos = computed(() => job.value.notes.filter((n) => n.severity === 'info'))

const CHIPS = {
  all: ['All', () => true],
  met: ['Met', (r) => r.status === 'met'],
  partial: ['Partial', (r) => r.status === 'partial'],
  missing: ['Missing', (r) => r.status === 'missing'],
  must: ['Must', (r) => r.priority === 'must_have'],
  preferred: ['Preferred', (r) => r.priority === 'preferred'],
}
// ?term=<t> (from the Requirements page): only the requirements using that term
const termFilter = computed(() => route.query.term?.toString().toLowerCase() || '')
const hasTerm = (r) => !termFilter.value || r.terms.some((t) => t.term.toLowerCase() === termFilter.value)
const reqs = computed(() => job.value.requirements.filter((r) => CHIPS[reqChip.value][1](r) && hasTerm(r)))
const chipCount = (key) => job.value.requirements.filter((r) => CHIPS[key][1](r) && hasTerm(r)).length

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
  resume: { file: fileOf('en', 'resume'), published: job.value.resume_url },
  cover: { file: fileOf('en', 'cover'), published: job.value.cover_letter_url },
  french: { file: fileOf('fr', 'resume'), published: null },
}))
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

    <div class="links">
      <el-button link type="primary" @click="postingOpen = true">View posting</el-button>
      <a v-if="job.url" :href="job.url" target="_blank" rel="noopener">Original offer →</a>
      <a v-if="job.resume_url" :href="job.resume_url" target="_blank" rel="noopener">Published resume →</a>
      <a v-if="job.cover_letter_url" :href="job.cover_letter_url" target="_blank" rel="noopener">Published cover letter →</a>
    </div>

    <el-tabs v-model="tab">
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
          <div v-for="p in ['must_have', 'preferred']" v-else :key="p" class="cov">
            <span class="cov-label">{{ p === 'must_have' ? 'Must-have' : 'Preferred' }}</span>
            <template v-if="job.coverage[p].ratio != null">
              <el-progress :percentage="pct(job.coverage[p].ratio)" :color="barColor(job.coverage[p].ratio)"
                :stroke-width="10" class="cov-bar" />
              <span class="muted">met {{ job.coverage[p].met }} · partial {{ job.coverage[p].partial }}
                · missing {{ job.coverage[p].missing }}</span>
            </template>
            <span v-else class="muted">—</span>
          </div>
          <div class="muted small">Met + ½ partial per priority. A tailoring aid, not an ATS score.</div>
        </el-card>

        <el-card v-if="job.gaps.length" shadow="never" class="block">
          <template #header>Gaps to work on (must-have first) · {{ job.gaps.length }}</template>
          <el-table :data="job.gaps" max-height="420" size="small">
            <el-table-column prop="description" label="Requirement" min-width="200" />
            <el-table-column label="Priority" width="80">
              <template #default="{ row }">{{ PRIORITY[row.priority] }}</template>
            </el-table-column>
            <el-table-column label="Status" width="90">
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

        <el-card id="all-requirements" shadow="never" class="block">
          <template #header>All requirements</template>
          <div class="chips">
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
            <el-table-column prop="description" label="Requirement" min-width="220" />
            <el-table-column label="Priority" width="80">
              <template #default="{ row }">{{ PRIORITY[row.priority] }}</template>
            </el-table-column>
            <el-table-column label="Status" width="90">
              <template #default="{ row }"><el-tag size="small" :type="STATUS_TAG[row.status]">{{ row.status }}</el-tag></template>
            </el-table-column>
            <el-table-column label="Evidence (resume quote)" min-width="260">
              <template #default="{ row }">
                <span v-if="row.evidence">‘{{ row.evidence }}’</span><span v-else class="muted">—</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="7">
        <el-card shadow="never" class="block">
          <template #header>Files</template>
          <div class="lang">English</div>
          <div v-if="!job.files.en.length" class="muted">Not built yet</div>
          <div v-for="f in job.files.en" :key="f.path" class="file">
            <a :href="fileUrl(f)" target="_blank" rel="noopener">{{ KIND[f.kind] }}</a>
            <span class="muted"> · {{ f.pages ?? '?' }} page{{ f.pages === 1 ? '' : 's' }}</span>
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
            <span class="muted"> · {{ f.pages ?? '?' }} page{{ f.pages === 1 ? '' : 's' }}</span>
            <el-tag v-if="f.not_ready" size="small" type="warning">not ready</el-tag>
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
    <el-tab-pane :label="`Interview prep (${prep?.topics.length ?? 0})`" name="interview">
      <InterviewPrep v-if="prep" :prep="prep" :job="job" @open-doc="openDoc" @open-posting="postingOpen = true" />
    </el-tab-pane>
    </el-tabs>

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
        <el-tab-pane v-for="(label, key) in { resume: 'Resume', cover: 'Cover letter', french: 'French' }" :key="key"
          :label="label" :name="key">
          <template v-if="docs[key].file">
            <div class="drawer-actions">
              <a :href="fileUrl(docs[key].file)" :download="docs[key].file.name">Download</a>
              <a v-if="docs[key].published" :href="docs[key].published" target="_blank" rel="noopener">Published →</a>
            </div>
            <iframe v-if="docsOpen && docTab === key" :src="fileUrl(docs[key].file)" class="pdf" :title="label" />
          </template>
          <div v-else class="muted">
            {{ key === 'french' && !job.french_version ? 'Not needed (English posting).' : 'Not built yet.' }}
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
.meta { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; color: #606266; font-size: 14px; }
.head-actions { display: flex; gap: 8px; margin-top: 12px; }
.links { display: flex; gap: 20px; align-items: center; margin: 16px 0; font-size: 14px; }
.links a, .drawer-actions a, .file a { color: var(--el-color-primary); text-decoration: none; }
.block { margin-bottom: 16px; }
.note { display: flex; gap: 8px; align-items: baseline; margin: 6px 0; font-size: 14px; }
.note-text { flex: 1; }
.small { font-size: 12px; margin-top: 8px; }
.cov { display: flex; gap: 12px; align-items: center; margin: 8px 0; font-size: 14px; }
.cov-label { width: 80px; }
.cov-bar { width: 220px; }
.chips { display: flex; gap: 8px; margin-bottom: 8px; }
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
