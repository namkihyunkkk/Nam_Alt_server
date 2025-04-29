# filename: okx_server.py

from fastapi import FastAPI, Query
import hmac
import hashlib
import base64
import time
import requests
import os



app = FastAPI()

# ✅ 너의 OKX API 정보
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
PASSPHRASE = os.getenv("PASSPHRASE")

BASE_URL = "https://www.okx.com"

def generate_headers(method: str, endpoint: str):
    timestamp = str(time.time())
    prehash = f"{timestamp}{method}{endpoint}"
    signature = base64.b64encode(
        hmac.new(SECRET_KEY.encode(), prehash.encode(), hashlib.sha256).digest()
    ).decode()

    return {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
    }

@app.get("/price")
def get_price(symbol: str = Query("BTC-USDT-SWAP")):
    endpoint = f"/api/v5/market/ticker?instId={symbol}"
    headers = generate_headers("GET", endpoint)
    url = BASE_URL + endpoint
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return {
            "symbol": symbol,
            "last": data["data"][0]["last"],
            "ask": data["data"][0]["askPx"],
            "bid": data["data"][0]["bidPx"],
            "vol": data["data"][0]["vol24h"],
            "change": data["data"][0]["change24h"],
        }
    else:
        return {"error": response.text}
