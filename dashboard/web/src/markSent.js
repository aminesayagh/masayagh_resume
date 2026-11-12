// "Mark as sent": pick the day it was sent (today by default, never in the future), then run src/offers.py sent.
import { h } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const today = () => new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10)

export async function markSent(job, onDone) {
  let day = today()
  try {
    await ElMessageBox({
      title: 'Mark as sent',
      message: h('div', [
        h('p', { style: 'margin-top: 0' },
          `${job.company} · ${job.role} (v${job.version}) will be frozen: no rebuild, edit or republish afterwards. ` +
          'To change it later, create a new version.'),
        h('label', { style: 'display: flex; gap: 8px; align-items: center' }, [
          'Sent on',
          h('input', { type: 'date', value: day, max: today(), class: 'el-input__inner sent-date',
                       onInput: (e) => { day = e.target.value } }),
        ]),
      ]),
      showCancelButton: true,
      confirmButtonText: 'Mark as sent',
      cancelButtonText: 'Cancel',
      beforeClose: (action, instance, done) => {
        if (action === 'confirm' && (!day || day > today())) {
          ElMessage.error('Pick a date that is not in the future')
          return
        }
        done()
      },
    })
  } catch {
    return // cancelled
  }
  try {
    const res = await fetch(`/api/jobs/${encodeURIComponent(job.slug)}/sent`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ date: day }),
    })
    const out = await res.json()
    if (!res.ok || !out.ok) throw new Error((typeof out.detail === 'string' && out.detail) || out.output || res.statusText)
    ElMessage.success(`Marked as sent on ${day}`)
    await onDone?.()
  } catch (e) {
    ElMessage.error({ message: e.message, duration: 6000 })
  }
}
