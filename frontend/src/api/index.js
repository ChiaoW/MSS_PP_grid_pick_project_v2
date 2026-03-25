import axios from 'axios';

// 建立 Axios 實體，並設定後端 API 的基礎路徑
// 開發階段預設對應本地端的 FastAPI
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json'
    },
    timeout: 15000 // 呼應原本 python requests 的 15 秒 timeout 設定
});

// 可在此處加入攔截器處理統一的錯誤捕捉，目前先保持單純
api.interceptors.response.use(
    response => response,
    error => {
        console.error("API 請求發生錯誤:", error);
        return Promise.reject(error);
    }
);

export default api;