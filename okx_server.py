from fastapi import FastAPI, Query
import hmac, hashlib, base64, time, requests, os

app = FastAPI()

# 환경변수로부터 OKX API 키 받기
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
PASSPHRASE = os.getenv("PASSPHRASE")
BASE_URL = "https://www.okx.com"

def generate_headers(method, endpoint):
    timestamp = str(time.time())
    prehash = f"{timestamp}{method}{endpoint}"
    signature = base64.b64encode(hmac.new(SECRET_KEY.encode(), prehash.encode(), hashlib.sha256).digest()).decode()

    return {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

@app.get("/price")
def get_price(symbol: str = Query(...)):
    endpoint = f"/api/v5/market/ticker?instId={symbol}"
    headers = generate_headers("GET", endpoint)
    url = BASE_URL + endpoint
    r = requests.get(url, headers=headers)
    return r.json()["data"][0] if r.status_code == 200 else {"error": r.text}

@app.get("/orderbook")
def get_orderbook(symbol: str = Query(...)):
    endpoint = f"/api/v5/market/books?instId={symbol}&sz=50"
    headers = generate_headers("GET", endpoint)
    url = BASE_URL + endpoint
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return {"error": r.text}

    data = r.json()["data"][0]
    bids = data["bids"]
    asks = data["asks"]

    bid_total = sum(float(b[1]) for b in bids)
    ask_total = sum(float(a[1]) for a in asks)
    total = bid_total + ask_total

    bid_ratio = round((bid_total / total) * 100, 2)
    ask_ratio = round((ask_total / total) * 100, 2)
    signal = "LONG" if bid_ratio >= 60 else "SHORT" if ask_ratio >= 60 else "NEUTRAL"

    return {
        "symbol": symbol,
        "bid_ratio_percent": bid_ratio,
        "ask_ratio_percent": ask_ratio,
        "signal": signal
    }

@app.get("/swap-instruments")
def get_swap_instruments():
    endpoint = "/api/v5/public/instruments?instType=SWAP"
    headers = generate_headers("GET", endpoint)
    url = BASE_URL + endpoint
    r = requests.get(url, headers=headers)
    return [x["instId"] for x in r.json()["data"] if x["instId"].endswith("USDT-SWAP")]
