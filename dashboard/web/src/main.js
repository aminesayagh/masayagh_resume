import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import JobsList from './pages/JobsList.vue'
import JobPage from './pages/JobPage.vue'
import Requirements from './pages/Requirements.vue'

// Keep "/" and "/job/<slug>": src/tailor.py and src/review_ats.py print links to them.
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: JobsList },
    { path: '/job/:slug/:tab(interview)?', component: JobPage }, // one record: switching tabs keeps the page
    { path: '/requirements', component: Requirements }, // /skills redirects here (server side)
  ],
})

createApp(App).use(router).use(ElementPlus).mount('#app')
