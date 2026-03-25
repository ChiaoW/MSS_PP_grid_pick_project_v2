import pandas as pd
from sqlalchemy.orm import Session
from app.core.api_client import fetch_data_from_api
from app.models.domain import AllocationLog
from app.models.schemas import RecommendationRequest

def get_dropdown_options():
    """抓取動態選單資料"""
    customer_data = fetch_data_from_api("/api/products/search/getAllCustomer")
    companies = set()
    customer_map = {}
    
    for row in customer_data:
        comp = row.get("custname")
        prod = row.get("prodname")
        if comp and prod:
            companies.add(comp)
            if comp not in customer_map:
                customer_map[comp] = []
            if prod not in customer_map[comp]:
                customer_map[comp].append(prod)
                
    companies = sorted(list(companies))
    
    route_data = fetch_data_from_api("/api/routes/search/getAllFlow")
    routes = []
    for row in route_data:
        route_val = row.get("route")
        if route_val:
            routes.append(route_val)
            
    if not routes:
        routes = ['Normal_PR', 'Normal_LK', 'EDS', 'ALD', 'Probing']
        
    return {
        "companies": companies,
        "customer_map": customer_map,
        "routes": sorted(routes)
    }

def get_production_grid_overview():
    """取得 Grid 狀態並標準化欄位"""
    data = fetch_data_from_api("/api/meshwipstatuses/search/getMeshWipStatus")
    if not data:
        return pd.DataFrame()
        
    df = pd.DataFrame(data)
    
    rename_map = {
        'gridid': 'grid_id',
        'gridtype': 'grid_type',
        'capacity': 'capacity',
        'islowpip': 'is_low_pip',
        'exclusivelotid': 'exclusive_lot_id',
        'currentsamplescount': 'current_samples_count',
        'assignedlotid': 'assigned_lot_id',
        'status': 'status'
    }
    
    existing_rename_map = {k: v for k, v in rename_map.items() if k in df.columns}
    df.rename(columns=existing_rename_map, inplace=True)
    
    expected_columns = {
        'grid_id': 'Unknown',
        'grid_type': 'Others',
        'current_samples_count': 0,
        'assigned_lot_id': '-',
        'is_low_pip': False,
        'exclusive_lot_id': None,
        'status': 'Standby'
    }
    
    for col, default_val in expected_columns.items():
        if col not in df.columns:
            df[col] = default_val
            
    return df

def calculate_recommendations(req: RecommendationRequest, db: Session):
    """執行推薦演算法"""
    df_all = get_production_grid_overview()
    candidates = []

    if df_all.empty:
        return candidates

    safe_route = req.route if req.route is not None else ""
    
    for _, grid in df_all.iterrows():
        is_valid = True

        # 1. 滿載過濾
        if grid['current_samples_count'] >= 8: 
            is_valid = False

        # 2. Low PIP 管制
        if req.is_low_pip:
            if not grid['is_low_pip'] or not req.lot_id.strip() or req.lot_id.strip() not in str(grid['exclusive_lot_id']):
                is_valid = False
        else:
            if grid['is_low_pip']: 
                is_valid = False

        # 3. Route 材質匹配
        if 'EDS' in safe_route or 'ALD' in safe_route:
            if req.require_solid_carbon:
                if 'Holey' in str(grid['grid_type']):
                    is_valid = False
            else:
                if 'Holey' not in str(grid['grid_type']):
                    is_valid = False
            
        if is_valid:
            score = 100
            reasons = ["Capacity allowed (not fully loaded)"]
            if req.is_low_pip:
                reasons.append("Meets the criteria for Low PIP private network and Lot ID binding.")

            if 'EDS' in safe_route or 'ALD' in safe_route:
                if req.require_solid_carbon:
                    reasons.append("Solid Carbon Compliant (Non-Holey).")
                else:
                    reasons.append("Meets default Holey material requirements for EDS/ALD.")

            if req.lot_id.strip() and req.lot_id.strip() in str(grid['assigned_lot_id']):
                score += 50
                reasons.append("Same Lot ID")
            
            # 整合資料庫學習分數計算
            count = db.query(AllocationLog).filter(
                AllocationLog.route == safe_route,
                AllocationLog.grid_type == grid['grid_type']
            ).count()
            
            bonus = min(count * 2, 20)
            score += bonus
            if bonus > 0: 
                reasons.append(f"AI Bonus (+{bonus})")
            
            candidates.append({
                'Grid ID': grid['grid_id'],
                'Grid Type': grid['grid_type'],
                'Slots': f"{grid['current_samples_count']}/8",
                'Score': score,
                'Reasons': ", ".join(reasons),
                'Raw_Status': grid['status']
            })

    # 依據分數降序排列
    candidates_sorted = sorted(candidates, key=lambda x: x['Score'], reverse=True)
    return candidates_sorted