import requests
import hashlib
from app.core.config import settings

def get_api_auth():
    """實作雙重 MD5 加密機制產生 hashpassword"""
    client_ip = settings.CLIENT_IP
    raw_password = settings.API_PASSWORD
    username = settings.API_USERNAME
    
    # 步驟一：Client IP MD5
    ip_md5 = hashlib.md5(client_ip.encode('utf-8')).hexdigest()
    # 步驟二：原始密碼 + IP MD5 後再 MD5
    combined_str = raw_password + ip_md5
    final_hash = hashlib.md5(combined_str.encode('utf-8')).hexdigest()
    
    return (username, final_hash)

def fetch_data_from_api(endpoint: str):
    """共用 API 呼叫函式，包含 15 秒 Timeout 防護"""
    url = f"{settings.API_BASE_URL}{endpoint}"
    
    try:
        response = requests.get(url, auth=get_api_auth(), timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API 請求失敗 ({endpoint}): {str(e)}")
        return []