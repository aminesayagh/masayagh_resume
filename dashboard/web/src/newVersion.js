// "New version": confirm, run src/new_job.py --from on the server, then open the new job.
import { h } from 'vue'
import { ElLoading, ElMessage, ElMessageBox } from 'element-plus'

export async function newVersion(job, router) {
  try {
    await ElMessageBox.confirm(
      `Copies ${job.company} · ${job.role} (v${job.version}) into its next version, keeping its tailoring ` +
      `(resume content and cover letters). This job stays exactly as it is${job.sent ? ' (sent, frozen)' : ''}. ` +
      'The new version is not sent, and its resume is built now, which can take a minute.',
      'New version', { confirmButtonText: 'Create new version', cancelButtonText: 'Cancel', type: 'info' })
  } catch {
    return // cancelled
  }
  const loading = ElLoading.service({ text: 'Creating the new version and building its resume…' })
  let body
  try {
    const res = await fetch(`/api/jobs/${encodeURIComponent(job.slug)}/new-version`, { method: 'POST' })
    body = await res.json()
    if (!res.ok) body = { ok: false, output: body.detail ?? `${res.status} ${res.statusText}` }
  } catch (e) {
    body = { ok: false, output: e.message }
  } finally {
    loading.close()
  }
  if (body.ok) {
    ElMessage.success(`Created ${body.slug}`)
    router.push(`/job/${body.slug}`)
    return
  }
  // Failed, or the folder was created but the build did not finish: show the script's own output.
  await ElMessageBox.alert(h('pre', { class: 'script-output' }, body.output || 'No output'),
    body.slug ? `Created ${body.slug}, but the script reported a problem` : 'New version failed',
    { type: 'error', customStyle: { maxWidth: '760px', width: '90vw' } }).catch(() => {})
  if (body.slug) router.push(`/job/${body.slug}`)
}
