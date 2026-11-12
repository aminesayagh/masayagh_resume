<script setup>
// Interview prep tab ( /job/<slug>/interview ): review/interview.json topics + the posting's skills with years.
// Read only: the notes box has no storage yet.
import { computed, ref } from 'vue'

const props = defineProps({ prep: { type: Object, required: true }, job: { type: Object, required: true } })
const emit = defineEmits(['open-doc', 'open-posting'])

const TYPES = {
  prepare_story: { label: 'story', card: 'Stories to prepare', sub: 'the story behind a resume line', tag: 'success' },
  prove_claim: { label: 'prove a claim', card: 'Claims to prove', sub: 'only claimed: bring an example', tag: 'warning' },
  gap: { label: 'gap', card: 'Gaps', sub: "honest answer: related work / how you'd learn", tag: 'danger' },
}
const STAR = 'Situation · Task · Action · Result · what you’d do differently'

const chip = ref('all')
const CHIPS = {
  all: ['All', () => true],
  stories: ['Stories', (t) => t.focus === 'prepare_story'],
  claims: ['Claims', (t) => t.focus === 'prove_claim'],
  gaps: ['Gaps', (t) => t.focus === 'gap'],
  must: ['Must-have', (t) => t.priority === 'must_have'],
}
const count = (key) => props.prep.topics.filter(CHIPS[key][1]).length
const topics = computed(() => props.prep.topics.filter(CHIPS[chip.value][1]))
</script>

<template>
  <el-empty v-if="!prep.exists" description="No interview prep for this job yet: it is written by the review." />

  <el-row v-else :gutter="20">
    <el-col :span="17">
      <el-row :gutter="12" class="cards">
        <el-col v-for="(t, focus) in TYPES" :key="focus" :span="8">
          <el-card shadow="never">
            <div class="card-label">{{ t.card }}</div>
            <div class="card-value">{{ prep.summary[focus] ?? 0 }}</div>
            <div class="muted small">{{ t.sub }}</div>
          </el-card>
        </el-col>
      </el-row>

      <div class="chips">
        <el-check-tag v-for="(c, key) in CHIPS" :key="key" :checked="chip === key" @change="chip = key">
          {{ c[0] }} {{ count(key) }}
        </el-check-tag>
      </div>

      <el-empty v-if="!topics.length" description="No topic here" :image-size="60" />
      <el-card v-for="t in topics" :key="t.id" shadow="never" class="topic">
        <div class="topic-head">
          <b>{{ t.requirement }}</b>
          <el-tag size="small" :type="TYPES[t.focus]?.tag" round>{{ TYPES[t.focus]?.label ?? t.focus }}</el-tag>
          <el-tag size="small" type="info" round>{{ t.priority === 'must_have' ? 'must-have' : 'preferred' }}</el-tag>
        </div>
        <p><span class="muted">Posting:</span> ‘{{ t.posting_says }}’</p>
        <p>
          <span class="muted">Resume: </span>
          <template v-if="t.your_resume_says?.length">‘{{ t.your_resume_says.join(' … ') }}’</template>
          <template v-else>nothing yet</template>
        </p>
        <p v-if="t.focus === 'prepare_story'" class="star">STAR: {{ STAR }}</p>
        <el-input type="textarea" :rows="2" disabled placeholder="My notes (not wired yet: no storage)" />
      </el-card>
    </el-col>

    <el-col :span="7">
      <el-card shadow="never" class="block">
        <template #header>Skills to prepare</template>
        <div class="muted small">asked by the posting · your years</div>
        <div v-if="!prep.skills.length" class="muted">No resume skill matches the posting's terms.</div>
        <div v-for="s in prep.skills" :key="s.name" class="skill">
          <span>{{ s.name }}</span>
          <span :class="{ muted: s.years === 'start date needed' }">{{ s.years }}</span>
        </div>
      </el-card>
      <el-card shadow="never" class="block">
        <template #header>Before the interview</template>
        <div class="shortcuts">
          <el-button link type="primary" @click="emit('open-doc', 'resume')">Open the {{ job.sent ? 'sent ' : '' }}resume</el-button>
          <el-button link type="primary" @click="emit('open-doc', 'cover')">Open the {{ job.sent ? 'sent ' : '' }}cover letter</el-button>
          <el-button link type="primary" @click="emit('open-posting')">Re-read the posting</el-button>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
.cards { margin-bottom: 16px; }
.card-label { font-size: 13px; color: #606266; }
.card-value { font-size: 28px; font-weight: 600; margin: 4px 0; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.small { font-size: 12px; margin: 6px 0 12px; }
.topic { margin-bottom: 12px; font-size: 14px; }
.topic p { margin: 6px 0; }
.topic-head { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.star { color: var(--el-color-success-dark-2); font-size: 13px; }
.block { margin-bottom: 16px; }
.skill { display: flex; justify-content: space-between; font-size: 14px; margin: 6px 0; }
.shortcuts { display: flex; flex-direction: column; align-items: flex-start; gap: 8px; }
.shortcuts .el-button + .el-button { margin-left: 0; }
</style>
