<template>
  <header class="topbar">
    <span class="brand">Resume pipeline</span>
    <router-link to="/" :class="{ active: $route.path === '/' || $route.path.startsWith('/job/') }">Jobs</router-link>
    <router-link to="/requirements">Requirements</router-link>
  </header>
  <main class="page"><router-view /></main>
</template>

<style>
body { margin: 0; font-family: system-ui, sans-serif; background: #f6f7f9; color: #1f2329; }
.topbar { display: flex; gap: 24px; align-items: center; padding: 12px 32px; background: #fff; border-bottom: 1px solid #e4e7ed; }
.topbar .brand { font-weight: 600; margin-right: 16px; }
.topbar a { color: #606266; text-decoration: none; }
.topbar a.router-link-exact-active, .topbar a.active { color: var(--el-color-primary); font-weight: 600; }
.page { max-width: 1280px; margin: 0 auto; padding: 24px 32px; }
.muted { color: #909399; }
.script-output { white-space: pre-wrap; max-height: 50vh; overflow: auto; font-size: 12px; margin: 0; }
</style>
