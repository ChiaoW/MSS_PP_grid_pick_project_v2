import { createApp } from 'vue';
import { createPinia } from 'pinia';
import './style.css';
import App from './App.vue';

const pinia = createPinia();
const app = createApp(App);

// 註冊 Pinia 狀態管理工具
app.use(pinia);
app.mount('#app');
