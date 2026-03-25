<template>
  <div class="min-h-screen bg-gray-50 p-6 text-gray-800">
    <div class="max-w-7xl mx-auto bg-white p-6 rounded-lg shadow-sm">
      <h1 class="text-3xl font-bold mb-6 text-gray-900">Smart Grid Allocator</h1>

      <div class="mb-8">
        <h2 class="text-xl font-semibold mb-4 border-b pb-2">Current Sample Information</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4 items-start">
          <div class="flex flex-col">
            <label class="text-sm font-medium text-gray-700 mb-1">Company</label>
            <select v-model="form.company" class="border border-gray-300 rounded p-2 focus:ring-2 focus:ring-blue-500 outline-none">
              <option value="">Choose an option</option>
              <option v-for="comp in store.companies" :key="comp" :value="comp">{{ comp }}</option>
            </select>
          </div>

          <div class="flex flex-col">
            <label class="text-sm font-medium text-gray-700 mb-1">Customer</label>
            <select v-model="form.customer" class="border border-gray-300 rounded p-2 focus:ring-2 focus:ring-blue-500 outline-none">
              <option value="">Choose an option</option>
              <option v-for="cust in customerOptions" :key="cust" :value="cust">{{ cust }}</option>
            </select>
          </div>

          <div class="flex flex-col">
            <label class="text-sm font-medium text-gray-700 mb-1">Route</label>
            <select v-model="form.route" class="border border-gray-300 rounded p-2 focus:ring-2 focus:ring-blue-500 outline-none">
              <option value="">Choose an option</option>
              <option v-for="route in store.routes" :key="route" :value="route">{{ route }}</option>
            </select>
          </div>

          <div class="flex flex-col">
            <label class="text-sm font-medium text-gray-700 mb-1">Lot ID</label>
            <input type="text" v-model="form.lot_id" placeholder="Enter Lot ID" class="border border-gray-300 rounded p-2 focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>

          <div class="flex flex-col pt-6 gap-2">
            <label class="inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="form.is_low_pip" class="form-checkbox h-4 w-4 text-blue-600 rounded border-gray-300">
              <span class="ml-2 text-sm text-gray-700">Requires Low PIP</span>
            </label>
            <label class="inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="form.require_solid_carbon" class="form-checkbox h-4 w-4 text-blue-600 rounded border-gray-300">
              <span class="ml-2 text-sm text-gray-700">Requires Solid Carbon</span>
            </label>
          </div>
        </div>

        <div class="mt-6">
          <button @click="handleSearch" :disabled="store.isLoading" class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded transition-colors disabled:bg-blue-400">
            {{ store.isLoading ? 'Searching...' : 'Find Matching Grids' }}
          </button>
        </div>
        
        <p v-if="store.error" class="text-red-600 mt-2 text-sm">{{ store.error }}</p>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-4 border-b pb-2">Recommended Candidates</h2>
        
        <div v-if="store.candidates.length > 0" class="space-y-2">
          <div v-for="grid in store.candidates" :key="grid['Grid ID']" class="flex items-center justify-between border-b border-gray-100 py-3">
            
            <div class="group relative cursor-pointer inline-block">
              <span class="border-b border-dashed border-gray-400 text-lg">
                <span class="font-bold">{{ grid['Grid ID'] }}</span> ({{ grid['Slots'] }}) - {{ grid['Grid Type'] }}
              </span>
              
              <div class="invisible group-hover:visible opacity-0 group-hover:opacity-100 transition-opacity duration-200 absolute z-10 bg-gray-800 text-white text-sm p-3 rounded top-full left-0 mt-2 w-max max-w-md shadow-lg">
                <div class="font-bold mb-1">Reasons:</div>
                <div v-html="formatReasons(grid['Reasons'])"></div>
              </div>
            </div>

            <button @click="handleSelect(grid)" class="border border-gray-300 hover:bg-gray-100 text-gray-800 font-medium py-1 px-4 rounded transition-colors">
              Select
            </button>
          </div>
        </div>
        <div v-else-if="!store.isLoading" class="text-gray-500 text-sm">
          No suitable grids found. Please start a search.
        </div>
        <details class="mt-8 group" open>
          <summary class="text-xl font-semibold mb-4 border-b pb-2 cursor-pointer list-none flex items-center justify-between">
            Full Grid Inventory Status
            <span class="transition group-open:rotate-180">
              <svg fill="none" height="24" shape-rendering="geometricPrecision" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path></svg>
            </span>
          </summary>
          
          <div class="mt-4">
            <div class="flex flex-wrap gap-2 mb-4">
              <span class="bg-[#E3F2FD] text-black px-3 py-1 rounded text-sm">Standby (待命)</span>
              <span class="bg-[#A5D6A7] text-black px-3 py-1 rounded text-sm">On Going (進行中)</span>
              <span class="bg-[#FFCDD2] text-black px-3 py-1 rounded text-sm">Full (滿載)</span>
              <span class="bg-[#E1BEE7] text-black px-3 py-1 rounded text-sm">Hold (暫停)</span>
              <span class="bg-[#FFE0B2] text-black px-3 py-1 rounded text-sm">Pending (等待)</span>
              <span class="bg-[#90CAF9] text-black px-3 py-1 rounded text-sm">Rework (重工)</span>
              <span class="bg-[#FFF59D] text-black px-3 py-1 rounded text-sm">To ERP (轉拋)</span>
              <span class="bg-white border border-gray-300 text-black px-3 py-1 rounded text-sm">Done / Finished (完成)</span>
            </div>

            <div class="overflow-x-auto h-[400px] border border-gray-200 rounded">
              <table class="min-w-full text-left text-sm whitespace-nowrap">
                <thead class="sticky top-0 bg-gray-100 shadow-sm z-10">
                  <tr>
                    <th class="p-3 font-semibold text-gray-700">ID</th>
                    <th class="p-3 font-semibold text-gray-700">Type</th>
                    <th class="p-3 font-semibold text-gray-700">Low PIP</th>
                    <th class="p-3 font-semibold text-gray-700">Slots</th>
                    <th class="p-3 font-semibold text-gray-700">Raw Status</th>
                    <th class="p-3 font-semibold text-gray-700">Assigned Lot ID</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in store.inventory" :key="item.grid_id" :class="getRowStyle(item.status)" class="border-b border-gray-100/50 hover:opacity-90">
                    <td class="p-3 font-medium">{{ item.grid_id }}</td>
                    <td class="p-3">{{ item.grid_type }}</td>
                    <td class="p-3 font-bold">{{ item.is_low_pip ? 'O' : 'X' }}</td>
                    <td class="p-3">{{ item.current_samples_count }}/8</td>
                    <td class="p-3">{{ item.status }}</td>
                    <td class="p-3">{{ item.assigned_lot_id || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useGridStore } from './store/gridStore';

const store = useGridStore();

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

const getRowStyle = (status) => {
  const colorMap = {
    'On Going': 'bg-[#A5D6A7] text-black',
    'Standby': 'bg-[#E3F2FD] text-black',
    'Hold': 'bg-[#E1BEE7] text-black',
    'Pending': 'bg-[#FFE0B2] text-black',
    'Full': 'bg-[#FFCDD2] text-black',
    'Rework': 'bg-[#90CAF9] text-black',
    'To ERP': 'bg-[#FFF59D] text-black',
    'Done': 'bg-white text-black',
    'Finished': 'bg-white text-black'
  };
  return colorMap[status] || 'bg-white text-black';
};

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

// 處理選擇 Grid 動作 (對應原本記錄至 db 的邏輯)
const handleSelect = async (grid) => {
  try {
    await store.submitAllocation({
      grid_id: grid['Grid ID'],
      route: form.value.route || '',
      borrower: 'System_User', // 之後可改為從登入狀態取得
      grid_type: grid['Grid Type']
    });
    alert(`Selection recorded for Grid: ${grid['Grid ID']}`);
  } catch (error) {
    alert("Failed to record selection.");
  }
};

// 處理 Tooltip 文字斷行 (對應 Streamlit 中的 replace 邏輯)
const formatReasons = (reasons) => {
  if (!reasons) return '';
  let formatted = reasons.replace(/, /g, "<br>- ");
  if (!formatted.startsWith("- ")) {
    formatted = "- " + formatted;
  }
  return formatted;
};
</script>