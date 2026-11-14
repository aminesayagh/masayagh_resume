<script setup>
// Resume ( /resume ): the default resume bloc by bloc, as in dashboard-flow.excalidraw "Wireframe: Resume".
// Read: GET /api/resume. Writes run src/ scripts on the server: an edited line is a new candidate (src/master.py set
// line), an experience's first line (set new-line), a role or summary version (set role|summary),
// Re-score (src/score_bullet.py / src/score_summary.py rescore). Each line shows the candidate in use
// (src/pick.py: best review, English and French text); the slider browses its other candidates.
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import TermDrawer from '../components/TermDrawer.vue'

const route = useRoute()
const router = useRouter()
const resumeId = computed(() => route.params.id)
const data = ref(null)
const error = ref('')
async function load() {
  try {
    const res = await fetch(`/api/resumes/${resumeId.value}`)
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    data.value = await res.json()
  } catch (e) {
    error.value = `Could not load the resume: ${e.message}`
  }
}

// ---- filter from the summary cards
const filter = ref('all')
const FILTERS = {
  all: () => true,
  revise: (c) => c.review?.verdict === 'Revise',
  ready: (c) => c.review?.verdict === 'Ready',
  unscored: (c) => !c.review,
}
const setFilter = (f) => { filter.value = filter.value === f ? 'all' : f }

// ---- candidates: one slider position per line (0 = newest); opens on the one in use
const shown = reactive({})
const open = ref(null) // the activity id of the expanded line
const keyOf = (line) => line.key ?? line.activity_id  // one slider per line of this resume
const index = (line) => shown[keyOf(line)] ?? Math.max(0, line.candidates.findIndex((c) => c.used))
const current = (line) => line.candidates[index(line)]
const slide = (line, step) => {
  const n = line.candidates.length
  shown[keyOf(line)] = (index(line) + step + n) % n
}
const visibleLines = (exp) => exp.lines.filter((l) => FILTERS[filter.value](current(l)))

const CRIT = ['result', 'evidence', 'contribution', 'clarity']
const dots = (v) => (v == null ? 'n/a' : '●'.repeat(v) + '○'.repeat(2 - v))
// Under every text field: characters and words, against the style check's word limit (src/check_style.py)
const count = (text, limit) => {
  const t = (text || '').trim(), words = t ? t.split(/\s+/).length : 0
  return `${t.length} characters · ${words}${limit ? ` / ${limit}` : ''} words${limit && words > limit ? ' · over the limit' : ''}`
}
// Only what goes wrong gets a colour: 0 / failed = red, 1 / partial = orange; the rest stays black and grey
const lvl = (v) => (v === 0 ? 'bad' : v === 1 ? 'warn' : '')
const cap = (t) => (t ? t[0].toUpperCase() + t.slice(1) : t)
const kwLabel = (k) => (k.status === 'new' ? `+ ${k.name}` : k.name)
// Skill chips open the same term drawer as the Requirements page (type, dates, keywords, merge, set aside)
const termOpen = ref(false)
const drawerTerm = ref(null)
const openTerm = (name) => { drawerTerm.value = name.toLowerCase(); termOpen.value = true }
const span = (m) => {
  if (!m) return ''
  const y = Math.floor(m / 12), r = m % 12
  return [y && `${y} yr`, r && `${r} mo`].filter(Boolean).join(' ')
}
const scoreOf = (c) => (c.review ? `${c.review.total}/8 · ${c.review.verdict}` : 'not scored')

// ---- table of contents: a click scrolls; the section in view gets the blue bar
const toc = computed(() => {
  if (!data.value) return []
  return [
    { id: 'profile', label: 'Profile' },
    { id: 'experience', label: `Experience · ${data.value.experiences.length}` },
    ...data.value.experiences.map((e) => ({
      id: `exp-${e.id}`, label: e.company, sub: true,
      tag: e.lines.length ? `${e.lines.length} line${e.lines.length > 1 ? 's' : ''}` : 'no lines',
    })),
    ...Object.entries(data.value.blocs).map(([k, v]) => ({ id: k, label: `${k[0].toUpperCase()}${k.slice(1)} · ${v.length}` })),
  ]
})
const inView = ref('profile')
const go = (id) => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
let observer
onMounted(async () => {
  await load()
  await nextTick()
  observer = new IntersectionObserver((entries) => {
    const top = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0]
    if (top) inView.value = top.target.id
  }, { rootMargin: '-10% 0px -70% 0px' })
  toc.value.forEach((t) => { const el = document.getElementById(t.id); if (el) observer.observe(el) })
})
onBeforeUnmount(() => observer?.disconnect())

// ---- writes
const busy = ref(false)
async function post(url, body) {
  busy.value = true
  try {
    const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body ?? {}) })
    const out = await res.json()
    if (!res.ok || !out.ok) throw new Error(out.detail || out.output || res.statusText)
    ElMessage.success('Done')
    await load()
    return true
  } catch (e) {
    ElMessage({ type: 'error', message: e.message, duration: 8000, showClose: true })
    return false
  } finally {
    busy.value = false
  }
}
// Editable texts: a draft per text (the summary, or one candidate of a line), compared with the saved one.
const drafts = reactive({})
const draft = (key, en, fr) => (drafts[key] ??= { en, fr, en0: en, fr0: fr })
const changed = (d) => d.en.trim() !== d.en0 || d.fr.trim() !== d.fr0
const reset = (d) => Object.assign(d, { en: d.en0, fr: d.fr0 })
const lineDraft = (line) => draft(`${keyOf(line)}-${current(line).id}`, current(line).text, current(line).fr)
// The role and the summary are blocs too: their versions slide and edit like a line's candidates.
const summaryBloc = computed(() => ({ activity_id: 'summary', ...data.value.profile.summary }))
async function saveLine(line) {  // an edited line is a new candidate: the old one is kept, the scores decide
  const d = lineDraft(line)
  if (await post(`/api/resumes/${resumeId.value}/edit`, { bloc: String(line.activity_id), en: d.en.trim(), fr: d.fr.trim(), position: line.position ?? null })) {
    reset(d)
    delete shown[keyOf(line)]
  }
}
async function saveProfile(bloc) {  // a new version of the role or summary: the old ones are kept
  const d = lineDraft(bloc)
  if (await post(`/api/resumes/${resumeId.value}/edit`, { bloc: bloc.activity_id, en: d.en.trim(), fr: d.fr.trim() })) {
    reset(d)
    delete shown[keyOf(bloc)]
  }
}
const dialog = reactive({ open: false, url: '', id: 0, title: '', en: '', fr: '' })
const addFirstLine = (exp) => Object.assign(dialog, { open: true, url: '/api/resume/new-line', id: exp.id,
  title: `New line · ${exp.company}`, en: '', fr: '' })
async function saveCandidate() {
  if (await post(dialog.url, { id: dialog.id, en: dialog.en.trim(), fr: dialog.fr.trim() })) dialog.open = false
}
const rescore = (c) => post('/api/resume/rescore', { id: c.id })
// This resume's own actions (src/resumes.py): switch a bloc's candidate, new version
const sent = computed(() => !!data.value?.resume?.sent)
async function useCandidate(line) {
  const bloc = ['role', 'summary'].includes(line.activity_id) ? line.activity_id : String(line.activity_id)
  if (await post(`/api/resumes/${resumeId.value}/switch`, { bloc, candidate: current(line).id, position: line.position ?? null }))
    delete shown[keyOf(line)]
}
async function newVersion() {
  busy.value = true
  try {
    const res = await fetch('/api/resumes', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ from_id: Number(resumeId.value), offer_id: data.value.resume.offer_id }) })
    const out = await res.json()
    if (!res.ok || !out.ok) throw new Error(out.detail || out.output || res.statusText)
    router.push(`/resumes/${out.id}`)
  } catch (e) {
    ElMessage({ type: 'error', message: e.message, duration: 8000, showClose: true })
  } finally {
    busy.value = false
  }
}
// Preview: a temporary PDF of this resume with the version shown in a slider swapped in (nothing is saved)
const pv = reactive({ open: false, loading: false, url: '', pages: 0, max: 3, label: '', error: '' })
async function openPreview(line = null) {
  const c = line && current(line)
  const swap = c && !c.used
  Object.assign(pv, { open: true, loading: true, url: '', error: '',
    label: !line ? 'This resume as it is' : swap ? `With this version of “${line.label || cap(line.activity_id)}”` : 'This resume (the version in use)' })
  const bloc = line && (['role', 'summary'].includes(line.activity_id) ? line.activity_id : String(line.activity_id))
  try {
    const res = await fetch(`/api/resumes/${resumeId.value}/preview`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(swap ? { bloc, candidate: c.id, position: line.position ?? null } : {}) })
    const out = await res.json()
    if (!res.ok || !out.ok) throw new Error(out.detail || out.output || res.statusText)
    Object.assign(pv, { url: out.url, pages: out.pages, max: out.max_pages })
  } catch (e) {
    pv.error = e.message
  } finally {
    pv.loading = false
  }
}
async function deleteVersion(bloc) {
  const c = current(bloc)
  try {
    await ElMessageBox.confirm('Delete this summary version? It leaves the candidates; a sent resume that used it keeps its record.',
      'Delete', { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' })
  } catch { return }
  if (await post(`/api/resumes/versions/${c.id}/delete`)) delete shown[keyOf(bloc)]
}
// Copy prompt: everything a fresh AI chat needs to propose better versions of one text (nothing is sent from here)
const BULLET_RUBRIC = `Each criterion scores 0 (missing), 1 (partial) or 2 (clear):
- Result: what improved, what became possible, or why the delivery mattered (not just a duty or a deliverable).
- Evidence: a meaningful metric, adoption count, milestone or concrete scope that lets a reader judge the result.
- Contribution: what the candidate personally built, designed, changed or led (not "helped with").
- Clarity: a recruiter grasps the main point on the first read, with no unexplained jargon.
The line is "Ready" when Result, Contribution and Clarity are 2, Evidence is at least 1, and the evidence supports the claim.
It follows the XYZ formula: accomplished X, as measured by Y, by doing Z.`
const SUMMARY_RUBRIC = `Name / Fame / Aim, each 0, 1 or 2:
- Name: a clear professional role paired with a specific area of work, type of product, or problem solved.
- Fame: what makes the positioning credible. One short credibility marker is enough (years of experience, a domain,
  a named product or client, a scale, or one result); a summary does not tell a full project story, which belongs
  in the experience section.
- Aim: where the candidate wants to apply this experience next, specific and connected to the experience
  (or unnecessary when the opening already makes the intended work clear).
Clarity passes when the positioning can be restated in one sentence. "Ready" needs Name 2, Fame 2, Aim 2 (or not
needed) and clarity passing.`
const offerBlock = () => {
  const r = data.value.resume
  if (!r?.offer) return 'This resume is not written for a specific job offer: keep it broadly relevant to the role.'
  return `This resume is written for this job offer: ${r.offer}.` +
    (r.must_have?.length ? `\nMust-have requirements (posting keywords): ${r.must_have.join(', ')}.` : '') +
    (r.preferred?.length ? `\nPreferred: ${r.preferred.join(', ')}.` : '') +
    `\nUse the posting's own words where the candidate truthfully has the skill; never add a skill that is not supported.`
}
const reviewBlock = (rev, kind) => {
  if (!rev) return 'It has not been reviewed yet.'
  if (kind === 'summary') {
    const parts = ['name', 'fame', 'aim'].map((k) => `- ${cap(k)}: ${rev[k].score ?? 'not needed'}/2` +
      (rev[k].quote ? ` (based on: "${rev[k].quote}")` : ''))
    return `Current review: ${cap(rev.verdict)}.\n${parts.join('\n')}\n- Clarity: ${rev.clarity.passes ? 'passes' : 'fails'}` +
      (rev.revision_requests.length ? `\nWhat to fix:\n${rev.revision_requests.map((r) => `- ${cap(r.criterion)}: ${r.request}`).join('\n')}` : '')
  }
  const parts = CRIT.map((k) => `- ${cap(k)}: ${rev.scores[k]}/2` + (rev.supporting_phrases[k] ? ` (based on: "${rev.supporting_phrases[k]}")` : ''))
  return `Current review: ${rev.total}/8, ${rev.verdict}. Claim–evidence match: ${rev.claim_evidence_match}.\n${parts.join('\n')}` +
    (rev.revision_requests.length ? `\nWhat to fix:\n${rev.revision_requests.map((r) => `- ${r}`).join('\n')}` : '')
}
const OUTPUT = (words) => `Your answer:
1. Start with a short list of the facts that would make it stronger and that you do not have (numbers, scale, users,
   outcome, tools). Do not wait for my answer: continue with the options. Never invent facts, numbers, clients, tools
   or results: where a fact is missing, write a clear placeholder such as [number of users] so I can fill it in or remove it.
2. Give 3 options. Each option: the English text (at most ${words} words, one sentence or two, no first person),
   its French translation, and one line saying which issue from the review it fixes.
3. Keep only what is true in the current version; you may reorder, tighten or reword it.`
function promptForLine(e, line) {
  const c = current(line)
  const others = e.lines.filter((l) => keyOf(l) !== keyOf(line)).map((l) => `- ${current(l).text}`).join('\n')
  return `You are an expert resume writer and recruiter for software engineering roles. Help me improve one line of my
resume. It is written in English, for recruiters and applicant tracking systems.

The line is ${line.kind === 'description' ? 'the one-sentence description of this experience' : 'one bullet point of this experience'}:
${e.company} — ${e.role}, ${e.from} to ${e.to || 'present'}.

Current text:
"${c.text}"

The other lines of the same experience (do not repeat them):
${others || '- none'}

${offerBlock()}

How the line is reviewed:
${BULLET_RUBRIC}

${reviewBlock(c.review, 'line')}

${OUTPUT(data.value.limits.bullet)}`
}
function promptForSummary(bloc) {
  const c = current(bloc)
  const role = (data.value.profile.role.candidates.find((x) => x.used) || {}).text || ''
  const exps = data.value.experiences.filter((e) => e.lines.length)
    .map((e) => `- ${e.company} — ${e.role}, ${e.from} to ${e.to || 'present'}: ${e.lines.map((l) => current(l).text).join(' ')}`).join('\n')
  return `You are an expert resume writer and recruiter for software engineering roles. Help me improve the summary at
the top of my resume (2 to 4 lines under my name and title). It is written in English, for recruiters and applicant
tracking systems.

My title on the resume: ${role}

Current summary:
"${c.text}"

My experience, as it appears on the resume (use it only as the source of true facts):
${exps}

${offerBlock()}

How the summary is reviewed:
${SUMMARY_RUBRIC}

${reviewBlock(c.review, 'summary')}

${OUTPUT(data.value.limits.summary)}`
}
async function copyPrompt(text) {
  try {
    await navigator.clipboard.writeText(text)
  } catch {
    const t = document.createElement('textarea')
    t.value = text
    document.body.appendChild(t)
    t.select()
    document.execCommand('copy')
    t.remove()
  }
  ElMessage.success('Prompt copied')
}
const rescoreSummary = () => post('/api/resume/summary/rescore', { id: current(summaryBloc.value).id })
</script>

<template>
  <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
  <div v-else-if="!data" class="muted">Loading…</div>
  <template v-else>
    <!-- this resume: name, offer, status, actions -->
    <div class="resume-head">
      <div>
        <router-link to="/resumes" class="small muted">← Resumes</router-link>
        <h1>{{ data.resume.name }}</h1>
        <div class="muted small">{{ data.resume.offer || 'No job offer' }} · created {{ data.resume.created }}
          · {{ data.resume.sent ? `Sent ${data.resume.sent} (read-only)` : 'Draft' }}</div>
      </div>
      <div class="row">
        <el-button size="small" @click="openPreview()">Preview</el-button>
        <el-button size="small" :loading="busy" @click="newVersion">New version</el-button>
      </div>
    </div>
    <!-- 1 summary cards: click = filter -->
    <div class="cards">
      <el-card v-for="c in [
        { f: 'all', label: 'Lines scored', big: data.score.scored, sub: `of ${data.score.lines} on the resume` },
        { f: 'ready', label: 'Ready', big: data.score.ready, sub: 'pass every rubric check' },
        { f: 'revise', label: 'Revise', big: data.score.scored - data.score.ready, sub: 'have revision requests' },
        { f: 'unscored', label: 'Average total', big: data.score.average != null ? `${data.score.average} / 8` : '—',
          sub: data.score.unscored ? `${data.score.unscored} not scored · click to show them` : 'of the saved scores' },
      ]" :key="c.f" shadow="hover" :class="['card', { on: filter === c.f && c.f !== 'all' }]" @click="setFilter(c.f)">
        <div class="card-label">{{ c.label }}</div>
        <div :class="['card-big', { red: c.red && c.big }]">{{ c.big }}</div>
        <div class="muted small">{{ c.sub }}</div>
      </el-card>
    </div>

    <div class="layout">
      <!-- sidebar: resume score + table of contents -->
      <aside class="side">
        <el-card shadow="never">
          <div class="h">Resume score</div>
          <div class="big">{{ data.score.max ? `${Math.round(100 * data.score.total / data.score.max)}%` : '—' }}</div>
          <el-tag type="info" effect="plain">
            {{ data.score.verdict }} · {{ data.score.ready }} of {{ data.score.lines }} lines Ready</el-tag>
          <div v-for="[k, v] in Object.entries(data.score.criteria).sort((a, b) => a[1] - b[1])" :key="k" class="crit">
            <span>{{ cap(k) }}</span>
            <el-progress :percentage="v * 50" :show-text="false" :stroke-width="8"
              :color="v < 1 ? '#f56c6c' : v < 1.5 ? '#e6a23c' : '#67c23a'" />
            <span class="muted">{{ v }}</span>
          </div>
        </el-card>
        <el-card shadow="never" class="toc">
          <div class="h">On this page</div>
          <a v-for="t in toc" :key="t.id" :class="['toc-item', { sub: t.sub, here: inView === t.id }]" @click="go(t.id)">
            <span>{{ t.label }}</span>
            <span v-if="t.tag" class="small muted">{{ t.tag }}</span>
          </a>
        </el-card>
      </aside>

      <section class="main">
        <!-- profile: role and summary, each with its versions -->
        <el-card id="profile" shadow="never" class="block">
          <template #header>Profile</template>
          <div v-for="bloc in [summaryBloc]" :key="bloc.activity_id" class="profile-bloc">
            <div class="row">
              <span class="lbl">{{ bloc.activity_id === 'role' ? 'Role' : 'Summary' }}</span>
              <el-button-group size="small">
                <el-button :disabled="bloc.candidates.length < 2" @click="slide(bloc, -1)">‹</el-button>
                <el-button disabled>{{ index(bloc) + 1 }} / {{ bloc.candidates.length }}</el-button>
                <el-button :disabled="bloc.candidates.length < 2" @click="slide(bloc, 1)">›</el-button>
              </el-button-group>
              <el-tag v-if="current(bloc).used" size="small" type="info">In use</el-tag>
              <el-button v-else-if="!sent" size="small" :loading="busy" @click="useCandidate(bloc)">Use in this resume</el-button>
              <el-button v-if="!current(bloc).open_uses" size="small" :loading="busy" @click="deleteVersion(bloc)">Delete</el-button>
              <el-tag v-else-if="!current(bloc).review && bloc.activity_id === 'summary'" size="small" type="info">Not reviewed yet</el-tag>
            </div>
            <el-alert v-if="bloc.warning" :title="bloc.warning" type="warning" :closable="false" show-icon />
            <el-input v-model="lineDraft(bloc).en" type="textarea" :autosize="{ minRows: bloc.activity_id === 'role' ? 1 : 3 }" maxlength="1200" />
            <template v-if="changed(lineDraft(bloc))">
              <div class="muted small fr-label">French</div>
              <el-input v-model="lineDraft(bloc).fr" type="textarea" :autosize="{ minRows: bloc.activity_id === 'role' ? 1 : 3 }" maxlength="1200" />
              <div class="count">{{ count(lineDraft(bloc).fr, bloc.activity_id === 'summary' ? data.limits.summary : null) }}</div>
            </template>
            <div class="row">
              <el-button size="small" type="primary" :loading="busy"
                :disabled="!changed(lineDraft(bloc)) || !lineDraft(bloc).en.trim() || !lineDraft(bloc).fr.trim()"
                @click="saveProfile(bloc)">Save</el-button>
              <el-button v-if="changed(lineDraft(bloc))" size="small" @click="reset(lineDraft(bloc))">Cancel</el-button>
              <span v-if="changed(lineDraft(bloc))" class="muted small">{{ sent ? 'Saved as a new version; this resume was sent and keeps its version.' : 'Saved as a new version and used in this resume; the current one is kept.' }}</span>
              <span class="grow" />
              <span class="count">{{ count(lineDraft(bloc).en, bloc.activity_id === 'summary' ? data.limits.summary : null) }}</span>
            </div>
          </div>
          <div class="chips"><span class="muted small">Keywords:</span>
            <el-tag v-for="k in data.profile.keywords" :key="k.name" size="small" class="kw" @click="openTerm(k.name)" type="info">{{ kwLabel(k) }}</el-tag>
          </div>
          <template v-for="rev in [current(summaryBloc).review]" :key="current(summaryBloc).id">
            <div class="review-grid" v-if="rev">
              <div>
                <div v-for="k in ['name', 'fame', 'aim', 'clarity']" :key="k"
                  v-show="k !== 'clarity' || rev.revision_requests.some((r) => r.criterion === 'clarity')" class="element">
                  <div class="element-name">{{ k }}</div>
                  <div v-if="k !== 'clarity'" class="small">Now: <span class="now">{{ rev[k].quote ? `“${rev[k].quote}”` : 'Nothing yet' }}</span></div>
                  <div v-for="(r, i) in rev.revision_requests.filter((r) => r.criterion === k)" :key="i" class="small proposal">
                    Proposal: {{ r.request }}</div>
                </div>
                <el-button size="small" :loading="busy" @click="rescoreSummary">Re-score</el-button>
                <el-button size="small" @click="copyPrompt(promptForSummary(summaryBloc))">Copy prompt</el-button>
              </div>
              <div class="panel">
                <div class="h">Summary review</div>
                <div :class="['verdict', rev.verdict === 'ready' ? 'green' : 'orange']">{{ cap(rev.verdict) }}</div>
                <div v-for="k in ['name', 'fame', 'aim']" :key="k" :class="['crit-line', lvl(rev[k].score)]">
                  {{ cap(k) }} <span>{{ dots(rev[k].score) }} {{ rev[k].score ?? '' }}</span></div>
                <div :class="['crit-line', rev.clarity.passes ? '' : 'bad']">Clarity <span>{{ rev.clarity.passes ? 'pass' : 'fail' }}</span></div>
              </div>
            </div>
            <div v-else class="dashed">This summary version has no review yet
              <el-button size="small" :loading="busy" @click="rescoreSummary">Review now</el-button>
              <el-button size="small" @click="copyPrompt(promptForSummary(summaryBloc))">Copy prompt</el-button></div>
          </template>
        </el-card>

        <!-- experience on the date rail -->
        <h2 id="experience">Experience</h2>
        <template v-for="e in data.experiences" :key="e.id">
          <div :id="`exp-${e.id}`" class="exp">
            <div class="rail"><div class="dates"><b>{{ e.to ?? 'present' }}</b><b>{{ e.from }}</b>
              <span class="muted small">{{ span(e.months) }}</span></div><i class="dot" /></div>
            <div class="exp-body">
              <div class="exp-head"><span class="h">{{ e.company }} — {{ e.role }}</span>
                <span class="muted small">{{ e.lines.length ? `${e.lines.length} line${e.lines.length > 1 ? 's' : ''}` : '' }}</span></div>

              <div v-if="!e.lines.length" class="dashed">No lines in the db yet ·
                <el-button size="small" link type="primary" @click="addFirstLine(e)">+ Add candidate</el-button></div>
              <template v-for="line in visibleLines(e)" :key="keyOf(line)">
                <div v-if="open !== keyOf(line)" class="line" @click="open = keyOf(line)">
                  <span class="line-text">{{ current(line).text }}</span>
                  <el-tag size="small" type="info">{{ scoreOf(current(line)) }}</el-tag>
                  <span class="muted small">{{ index(line) + 1 }}/{{ line.candidates.length }}</span>
                </div>
                <el-card v-else shadow="never" class="expanded">
                  <div class="row">
                    <el-button-group size="small">
                      <el-button :disabled="line.candidates.length < 2" @click.stop="slide(line, -1)">‹</el-button>
                      <el-button disabled>{{ index(line) + 1 }} / {{ line.candidates.length }}</el-button>
                      <el-button :disabled="line.candidates.length < 2" @click.stop="slide(line, 1)">›</el-button>
                    </el-button-group>
                    <el-tag v-if="current(line).used" size="small" type="info">In use</el-tag>
                    <el-button v-else-if="!sent" size="small" :loading="busy" @click.stop="useCandidate(line)">Use in this resume</el-button>
                    <span class="muted small">Keywords:</span>
                    <el-tag v-for="k in line.keywords" :key="k.name" size="small" class="kw" @click="openTerm(k.name)" type="info">{{ kwLabel(k) }}</el-tag>
                    <span class="grow" />
                    <el-button size="small" link @click="open = null">Collapse</el-button>
                  </div>
                  <el-alert v-if="line.warning" :title="line.warning" type="warning" :closable="false" show-icon />
                  <div class="review-grid">
                    <div>
                      <el-input v-model="lineDraft(line).en" type="textarea" :autosize="{ minRows: 2 }" maxlength="600" />
                      <template v-if="changed(lineDraft(line))">
                        <div class="muted small fr-label">French</div>
                        <el-input v-model="lineDraft(line).fr" type="textarea" :autosize="{ minRows: 2 }" maxlength="600" />
                        <div class="count">{{ count(lineDraft(line).fr, line.kind === 'bullet' ? data.limits.bullet : null) }}</div>
                      </template>
                      <div class="row">
                        <el-button size="small" type="primary" :loading="busy"
                          :disabled="!changed(lineDraft(line)) || !lineDraft(line).en.trim() || !lineDraft(line).fr.trim()"
                          @click="saveLine(line)">Save</el-button>
                        <el-button v-if="changed(lineDraft(line))" size="small" @click="reset(lineDraft(line))">Cancel</el-button>
                        <span v-if="changed(lineDraft(line))" class="muted small">{{ sent ? 'Saved as a new version; this resume was sent and keeps its version.' : 'Saved as a new version and used in this resume; the current one is kept.' }}</span>
                        <span class="grow" />
                        <span class="count">{{ count(lineDraft(line).en, line.kind === 'bullet' ? data.limits.bullet : null) }}</span>
                      </div>
                      <template v-if="current(line).review">
                        <div class="muted small">Phrases behind the scores:</div>
                        <div v-for="k in CRIT" :key="k" v-show="current(line).review.supporting_phrases[k]" class="quote">
                          {{ k }}: “{{ current(line).review.supporting_phrases[k] }}”</div>
                        <div class="sub">Revision requests</div>
                        <ul class="requests"><li v-for="(r, i) in current(line).review.revision_requests" :key="i">{{ r }}</li></ul>
                      </template>
                      <div class="row">
                        <el-button size="small" :loading="busy" @click="rescore(current(line))">Re-score</el-button>
                        <el-button size="small" @click="copyPrompt(promptForLine(e, line))">Copy prompt</el-button>
                      </div>
                    </div>
                    <div class="panel" v-if="current(line).review">
                      <div class="h">Review</div>
                      <div class="verdict orange">{{ current(line).review.total }} / 8 · {{ cap(current(line).review.verdict) }}</div>
                      <div v-for="k in CRIT" :key="k" :class="['crit-line', lvl(current(line).review.scores[k])]">
                        {{ cap(k) }} <span>{{ dots(current(line).review.scores[k]) }} {{ current(line).review.scores[k] }}</span></div>
                      <div class="muted small">Evidence type: {{ current(line).review.evidence_type }}</div>
                      <div :class="['small', { supports: '', partial: 'warn', missing: 'bad', mismatch: 'bad' }[current(line).review.claim_evidence_match]]">
                        Claim–evidence: {{ current(line).review.claim_evidence_match }}</div>
                      <div class="muted small">Attribution: {{ current(line).review.attribution }}</div>
                    </div>
                    <div v-else class="panel dashed">Not scored yet: it is used only when no candidate of this line is scored.</div>
                  </div>
                </el-card>
              </template>
            </div>
          </div>
          <div v-if="e.gap_after" class="exp">
            <div class="rail"><div class="dates"><b class="orange">{{ e.gap_after.from }}</b></div><i class="dot gap" /></div>
            <div class="exp-body"><div class="gapbox">
              <b>Gap: {{ e.gap_after.from === e.gap_after.to ? e.gap_after.from : `${e.gap_after.from} – ${e.gap_after.to}` }}
                · {{ span(e.gap_after.months) }} with no experience on the resume</b>
              <div class="muted small">between {{ e.gap_after.after }} (ended {{ e.gap_after.ended }}) and
                {{ e.gap_after.before }} (started {{ e.gap_after.started }})</div>
            </div></div>
          </div>
        </template>

        <!-- projects, education, languages, certifications: their keywords -->
        <h2>Projects, education, languages, certifications: their keywords</h2>
        <div class="muted small legend">Dashed: not a skill yet. Click a keyword to edit it.</div>
        <div class="blocs">
          <el-card v-for="(items, key) in data.blocs" :id="key" :key="key" shadow="never" class="bloc">
            <template #header>{{ key[0].toUpperCase() + key.slice(1) }}</template>
            <div v-for="i in items" :key="i.title" class="bloc-item">
              <div class="small">{{ i.title }}</div>
              <div class="chips">
                <el-tag v-for="k in i.keywords" :key="k.name" size="small" class="kw" @click="openTerm(k.name)" type="info" :effect="k.status === 'new' ? 'plain' : 'light'"
                  :class="{ newkw: k.status === 'new' }">{{ kwLabel(k) }}</el-tag>
                <span v-if="!i.keywords.length" class="muted small">no skill keyword found</span>
              </div>
            </div>
          </el-card>
        </div>
      </section>
    </div>

    <el-dialog v-model="dialog.open" :title="dialog.title" width="640px">
      <p class="muted small">A new candidate keeps the old ones. It is scored, then the best-reviewed one is used on the
        resume. Write only what is true; both languages are needed.</p>
      <el-form label-position="top">
        <el-form-item label="English"><el-input v-model="dialog.en" type="textarea" :rows="3" maxlength="600" show-word-limit /></el-form-item>
        <el-form-item label="French"><el-input v-model="dialog.fr" type="textarea" :rows="3" maxlength="600" show-word-limit /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.open = false">Cancel</el-button>
        <el-button type="primary" :loading="busy" :disabled="!dialog.en.trim() || !dialog.fr.trim()" @click="saveCandidate">Save candidate</el-button>
      </template>
    </el-dialog>
    <TermDrawer v-model="termOpen" :term="drawerTerm" @changed="load" />
    <el-drawer v-model="pv.open" size="85%" title="Preview" class="pv">
      <div v-if="pv.loading" class="muted">Building the PDF…</div>
      <el-alert v-else-if="pv.error" :title="pv.error" type="error" :closable="false" show-icon />
      <iframe v-else-if="pv.url" :src="pv.url" class="pv-frame" title="Resume preview" />
    </el-drawer>
  </template>
</template>

<style scoped>
.main, .side { line-height: 1.6; }
.cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.card { cursor: pointer; }
.card.on { border-color: #303133; }
.card-label { font-size: 14px; }
.card-big { font-size: 28px; font-weight: 600; margin: 4px 0; }
.layout { display: grid; grid-template-columns: 300px 1fr; gap: 20px; align-items: start; }
.side { position: sticky; top: 12px; display: flex; flex-direction: column; gap: 12px; max-height: calc(100vh - 24px); overflow: auto; }
.side > * { flex-shrink: 0; }
.h { font-weight: 600; }
.big { font-size: 26px; font-weight: 600; margin: 4px 0 8px; }
.pct { font-size: 16px; }
.sub { margin-top: 6px; font-size: 13px; color: #606266; }
.crit { display: grid; grid-template-columns: 100px 1fr 30px; gap: 8px; align-items: center; font-size: 13px; margin: 8px 0; }
.kw { cursor: pointer; }
.element { margin: 10px 0 16px; line-height: 1.6; }
.element-name { font-weight: 600; text-transform: capitalize; }
.now { color: #303133; }
.proposal { color: #606266; margin-top: 4px; }
.toc-item { display: flex; justify-content: space-between; gap: 8px; padding: 6px 8px; cursor: pointer; border-left: 3px solid transparent; font-size: 14px; }
.toc-item > span:last-child { white-space: nowrap; }
.toc-item.sub { padding-left: 18px; }
.toc-item.here { border-left-color: #303133; color: #303133; font-weight: 600; }
.main h2 { font-size: 20px; margin: 24px 0 8px; }
.block { margin-bottom: 8px; }
.row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin: 10px 0; }
.row .el-button + .el-button { margin-left: 0; }  /* the row's gap is the only space between buttons */
.lbl { width: 64px; color: #606266; font-size: 13px; }
.grow { flex: 1; }
.fr-label { margin-top: 6px; }
.count { font-size: 12px; color: #909399; text-align: right; margin-top: 2px; white-space: nowrap; }
.profile-bloc { margin-bottom: 14px; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin: 10px 0; }
.review-grid { display: grid; grid-template-columns: 1fr 300px; gap: 16px; margin-top: 8px; }
.panel { border: 1px solid var(--el-border-color); border-radius: 8px; padding: 12px; font-size: 14px; }
.verdict { font-size: 20px; font-weight: 600; margin: 6px 0 12px; }
.crit-line { display: flex; justify-content: space-between; margin: 4px 0; }
.quote { color: #606266; font-size: 13px; margin: 4px 0 4px 10px; }
.requests { color: #606266; font-size: 13px; padding-left: 20px; margin: 6px 0 12px; }
.requests li { margin-bottom: 6px; }
.dashed { border: 1px dashed #c0c4cc; border-radius: 6px; padding: 10px 12px; color: #909399; background: #fafafa; margin: 6px 0; }
.exp { display: grid; grid-template-columns: 130px 1fr; }
.rail { position: relative; border-right: 2px solid #dcdfe6; margin-right: 22px; }
.dates { display: flex; flex-direction: column; gap: 2px; color: #303133; font-size: 14px; padding-top: 2px; }
.dates b { font-weight: 500; }
.dot { position: absolute; right: -8px; top: 4px; width: 12px; height: 12px; border-radius: 50%; background: #909399; }
.dot.gap { background: #fff; border: 2px solid #909399; width: 10px; height: 10px; }
.exp-body { padding-bottom: 28px; min-width: 0; }
.exp-head { display: flex; justify-content: space-between; }
.line { display: flex; gap: 12px; align-items: center; background: #fff; border: 1px solid #e4e7ed; border-radius: 6px; padding: 10px 14px; margin: 8px 0; cursor: pointer; }
.line:hover { border-color: #909399; }
.line-text { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 14px; }
.expanded { border: 1px solid #909399; margin: 10px 0; }
.gapbox { border: 1px dashed #c0c4cc; color: #303133; border-radius: 6px; padding: 10px 14px; }
.blocs { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.bloc-item { margin-bottom: 10px; }
.newkw { border-style: dashed; }
.legend { margin-bottom: 8px; }
.small { font-size: 12px; }
.red, .green, .orange { color: inherit; }
.bad { color: #e5484d; }
.warn { color: #d97706; }
.resume-head { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; }
.resume-head h1 { font-size: 22px; margin: 4px 0; }
.pv-frame { width: 100%; height: calc(100vh - 90px); border: 0; }
</style>
