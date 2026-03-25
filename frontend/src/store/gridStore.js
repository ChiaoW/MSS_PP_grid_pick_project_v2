import { defineStore } from 'pinia';
import api from '../api/index.js';

export const useGridStore = defineStore('grid', {
    state: () => ({
        // 選單資料
        companies: [],
        customerMap: {},
        routes: [],
        
        // 推薦結果資料
        candidates: [],

        // 用來存放所有 Grid 狀態
        inventory: [], 
        
        // 系統狀態
        isLoading: false,
        error: null
    }),
    
    actions: {
        // 1. 取得動態選單選項
        async fetchOptions() {
            try {
                const response = await api.get('/options');
                this.companies = response.data.companies;
                this.customerMap = response.data.customer_map;
                this.routes = response.data.routes;
            } catch (error) {
                this.error = '無法取得選單資料';
            }
        },
        
        // 2. 傳送表單條件並取得推薦清單
        async fetchRecommendations(payload) {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await api.post('/recommendations', payload);
                this.candidates = response.data.candidates;
            } catch (error) {
                this.error = '推薦運算發生錯誤';
            } finally {
                this.isLoading = false;
            }
        },
        
        // 3. 記錄使用者的選擇 (Feedback Log)
        async submitAllocation(payload) {
            try {
                await api.post('/allocations', payload);
            } catch (error) {
                this.error = '記錄分配失敗';
                throw error; // 讓元件層能夠接住這個錯誤並顯示提示
            }
        },
        // 4. 取得所有 Grid 狀態
        async fetchInventory() {
            try {
                const response = await api.get('/inventory');
                this.inventory = response.data.items;
            } catch (error) {
                console.error("無法取得所有 Grid 狀態", error);
            }
        }
    }
});