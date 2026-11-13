import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import JobsList from './pages/JobsList.vue'
import JobPage from './pages/JobPage.vue'
import Requirements from './pages/Requirements.vue'
import Resume from './pages/Resume.vue'
import Resumes from './pages/Resumes.vue'

// Keep "/" and "/job/<slug>": src/tailor.py and src/review_ats.py print links to them.
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: JobsList },
    { path: '/job/:slug/:tab(interview|skills)?', component: JobPage }, // one record: switching tabs keeps the page
    { path: '/requirements', component: Requirements }, // /skills redirects here (server side)
    { path: '/resumes', component: Resumes },
    { path: '/resumes/:id', component: Resume },
    { path: '/resume', redirect: '/resumes' },
  ],
})

createApp(App).use(router).use(ElementPlus).mount('#app')
