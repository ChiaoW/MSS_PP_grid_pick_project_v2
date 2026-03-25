from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import schemas, domain
from app.core import services
import pandas as pd

router = APIRouter()

@router.get("/options", response_model=schemas.GridOptionResponse)
def get_options():
    """取得前端下拉式選單所需之公司、客戶、流程選項"""
    return services.get_dropdown_options()

@router.post("/recommendations", response_model=schemas.RecommendationResponse)
def get_recommendations(req: schemas.RecommendationRequest, db: Session = Depends(get_db)):
    """接收條件並回傳 Grid 推薦清單"""
    candidates = services.calculate_recommendations(req, db)
    return {"candidates": candidates}

@router.post("/allocations", response_model=schemas.BaseResponse)
def create_allocation(req: schemas.AllocationRequest, db: Session = Depends(get_db)):
    """記錄使用者的 Grid 選擇，作為後續演算法學習依據"""
    try:
        new_log = domain.AllocationLog(
            grid_id=req.grid_id,
            route=req.route,
            borrower=req.borrower,
            grid_type=req.grid_type
        )
        db.add(new_log)
        db.commit()
        return {"status": "success", "message": "Allocation recorded successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inventory", response_model=schemas.InventoryResponse)
def get_inventory():
    """取得所有 Grid 狀態總覽"""
    df = services.get_production_grid_overview()
    
    # 將 DataFrame 轉為字典清單
    items = df.to_dict(orient="records")
    
    # 處理 Pandas 中的 NaN 或 NaT，將其轉換為 Python 原生的 None
    for item in items:
        for key, value in item.items():
            if pd.isna(value):
                item[key] = None
                
    return {"items": items}