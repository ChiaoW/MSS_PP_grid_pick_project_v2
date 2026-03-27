<template>
  <div class="p-4 w-full">
    <div class="flex justify-between items-center border-b border-gray-200 pb-2 mb-4">
      <h1 class="text-xl text-gray-800">Smart Grid Allocator</h1>
    </div>

    <div class="space-y-4 mb-4">
      <div class="flex items-center">
        <label class="w-32 text-right pr-4 font-bold text-gray-700">Company</label>
        <select v-model="form.company" class="w-64 border border-[#ccc] rounded-[11px] px-3 py-[6px] focus:border-[#66afe9] focus:outline-none focus:shadow-[inset_0_1px_1px_rgba(0,0,0,0.075),0_0_8px_rgba(102,175,233,0.6)] transition-all bg-white">
          <option value="">Choose an option</option>
          <option v-for="comp in store.companies" :key="comp" :value="comp">{{ comp }}</option>
        </select>
      </div>

      <div class="flex items-center">
        <label class="w-32 text-right pr-4 font-bold text-gray-700">Customer</label>
        <select v-model="form.customer" class="w-64 border border-[#ccc] rounded-[11px] px-3 py-[6px] focus:border-[#66afe9] focus:outline-none focus:shadow-[inset_0_1px_1px_rgba(0,0,0,0.075),0_0_8px_rgba(102,175,233,0.6)] transition-all bg-white">
          <option value="">Choose an option</option>
          <option v-for="cust in customerOptions" :key="cust" :value="cust">{{ cust }}</option>
        </select>
      </div>

      <div class="flex items-center">
        <label class="w-32 text-right pr-4 font-bold text-gray-700">Route</label>
        <select v-model="form.route" class="w-64 border border-[#ccc] rounded-[11px] px-3 py-[6px] focus:border-[#66afe9] focus:outline-none focus:shadow-[inset_0_1px_1px_rgba(0,0,0,0.075),0_0_8px_rgba(102,175,233,0.6)] transition-all bg-white">
          <option value="">Choose an option</option>
          <option v-for="route in store.routes" :key="route" :value="route">{{ route }}</option>
        </select>
      </div>

      <div class="flex items-center">
        <label class="w-32 text-right pr-4 font-bold text-gray-700">Lot ID</label>
        <input type="text" v-model="form.lot_id" class="w-64 border border-[#ccc] rounded-[11px] px-3 py-[6px] focus:border-[#66afe9] focus:outline-none focus:shadow-[inset_0_1px_1px_rgba(0,0,0,0.075),0_0_8px_rgba(102,175,233,0.6)] transition-all" />
      </div>

      <div class="flex items-center mt-2">
        <div class="w-32"></div>
        <div class="flex-1 flex gap-6">
          <label class="inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="form.is_low_pip" class="form-checkbox h-4 w-4">
            <span class="ml-2">Requires Low PIP</span>
          </label>
          <label class="inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="form.require_solid_carbon" class="form-checkbox h-4 w-4">
            <span class="ml-2">Requires Solid Carbon</span>
          </label>
        </div>
      </div>
    </div>

    <div class="flex gap-1 ml-32 mb-4">
      <button @click="handleSearch" :disabled="store.isLoading" class="bg-[var(--color-brand-btn)] border border-[var(--color-brand-btn-border)] text-white px-[12px] py-[6px] rounded-[10px] hover:bg-[#286090] hover:border-[#204d74] disabled:opacity-65">
        {{ store.isLoading ? 'Querying...' : 'Query' }}
      </button>
      <button @click="exportToExcel" class="bg-[var(--color-brand-btn)] border border-[var(--color-brand-btn-border)] text-white px-[12px] py-[6px] rounded-[10px] hover:bg-[#286090] hover:border-[#204d74]">
        Export Excel
      </button>
    </div>

    <div v-if="store.error" class="text-[var(--color-danger-text)] font-bold mb-4 ml-2">
      <p>{{ store.error }}</p>
    </div>

    <div class="w-full mt-4">
      <ag-grid-vue
        theme="legacy"
        class="ag-theme-balham"
        style="width: 100%; height: 400px;"
        :columnDefs="columnDefs"
        :rowData="store.candidates"
        :defaultColDef="defaultColDef"
        :suppressCellFocus="true"
        :overlayNoRowsTemplate="noRowsTemplate"
        @cellClicked="onCellClicked"
        :pagination="true" 
        :paginationPageSize="10"
        :paginationPageSizeSelector="[10, 20, 50, 100]"
      >
      </ag-grid-vue>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useGridStore } from './store/gridStore';
import * as XLSX from 'xlsx';
import { AgGridVue } from 'ag-grid-vue3';

import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-balham.css';

ModuleRegistry.registerModules([ AllCommunityModule ]);

const store = useGridStore();

// 處理 Tooltip 文字斷行 (給 ag-grid 渲染 HTML 使用)
const formatReasons = (reasons) => {
  if (!reasons) return '';
  let formatted = reasons.replace(/, /g, "<br>- ");
  if (!formatted.startsWith("- ")) {
    formatted = "- " + formatted;
  }
  return formatted;
};

// 處理選擇 Grid 動作
const handleSelect = async (grid) => {
  try {
    await store.submitAllocation({
      grid_id: grid['Mesh'],
      route: form.value.route || '',
      borrower: 'System_User',
      grid_type: grid['Grid Type']
    });
    alert(`Selection recorded for Grid: ${grid['Mesh']}`);
  } catch (error) {
    alert("Failed to record selection.");
  }
};

// 監聽表格點擊事件，若點擊的是 Action 欄位，則觸發 handleSelect
const onCellClicked = (event) => {
  if (event.colDef.headerName === 'Action') {
    handleSelect(event.data);
  }
};

// ag-grid 欄位設定
const columnDefs = ref([
  { headerName: 'Mesh', field: 'Mesh', width: 150 },
  { headerName: 'Grid Type', field: 'Grid Type', width: 150 },
  { headerName: 'Slots', field: 'Slots', width: 100 },
  { 
    headerName: 'Mesh Details', 
    field: 'Reasons', 
    flex: 1, 
    autoHeight: true, 
    wrapText: true,
    cellRenderer: (params) => formatReasons(params.value)
  },
  {
    headerName: 'Action',
    width: 90,
    cellClass: 'action-btn-cell',
    cellRenderer: () => `<a href="#" class="company-btn">Select</a>`
  }
]);

// ag-grid 預設設定
const defaultColDef = ref({
  resizable: true,
  sortable: true
});

// 無資料時的顯示模板
const noRowsTemplate = ref(`
  <div class="inline-block border border-gray-300 rounded px-4 py-2 bg-white text-gray-500">
    No Rows To Show
  </div>
`);

// 綁定表單狀態
const form = ref({
  company: '',
  customer: '',
  route: '',
  lot_id: '',
  is_low_pip: false,
  require_solid_carbon: false
});

// 元件掛載時抓取選項
onMounted(() => {
  store.fetchOptions();
  store.fetchInventory();
});

// 當 Company 改變時，動態計算對應的 Customer 選項
const customerOptions = computed(() => {
  if (!form.value.company || !store.customerMap[form.value.company]) {
    return [];
  }
  return store.customerMap[form.value.company];
});

// 當 Company 改變時，清空已選擇的 Customer
watch(() => form.value.company, () => {
  form.value.customer = '';
});

// 處理搜尋動作
const handleSearch = async () => {
  const { company, customer, route, lot_id, is_low_pip } = form.value;

  if (is_low_pip && !lot_id.trim()) {
    alert("Please enter Lot ID when Requires Low PIP is checked.");
    return;
  }

  if (!company && !customer && !route && !lot_id.trim() && !is_low_pip) {
    alert("Please enter or select at least one condition before searching.");
    return;
  }
  
  await store.fetchRecommendations({
    company: form.value.company || null,
    customer: form.value.customer || null,
    route: form.value.route || '',
    lot_id: form.value.lot_id,
    is_low_pip: form.value.is_low_pip,
    require_solid_carbon: form.value.require_solid_carbon
  });
};

// 匯出 Excel 功能
const exportToExcel = () => {
  if (store.candidates.length === 0) {
    alert("No data to export.");
    return;
  }

  const dataToExport = store.candidates.map(grid => ({
    'Mesh': grid['Mesh'],
    'Grid Type': grid['Grid Type'],
    'Slots': grid['Slots'],
    'Mesh Details': grid['Reasons']
  }));

  const worksheet = XLSX.utils.json_to_sheet(dataToExport);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Mesh_Recommendations");

  const now = new Date();
  const dateString = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}`;
  const filename = `Mesh_Recommendations_${dateString}.xlsx`;

  XLSX.writeFile(workbook, filename);
};
</script>