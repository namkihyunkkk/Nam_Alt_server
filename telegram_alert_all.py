import time, requests

SERVER_URL = "https://nam-alt-server.onrender.com"
TELEGRAM_BOT_TOKEN = "7991943781:AAE266OFk8JQFcL-qNwTZfF9UL_2T2zlH5c"
TELEGRAM_CHAT_ID = "5962630890"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

def check_orderbook(symbol):
    try:
        r = requests.get(f"{SERVER_URL}/orderbook", params={"symbol": symbol})
        data = r.json()
        bid = data["bid_ratio_percent"]
        ask = data["ask_ratio_percent"]
        signal = data["signal"]
        if bid >= 60 or ask >= 60:
            msg = f"*[{symbol}]*\n🟢 Bid: {bid}%\n🔴 Ask: {ask}%\n🚨 *{signal} SIGNAL*"
            send_telegram_message(msg)
    except:
        pass

def main():
    while True:
        try:
            res = requests.get(f"{SERVER_URL}/swap-instruments")
            symbols = res.json()
            for s in symbols:
                check_orderbook(s)
                time.sleep(0.5)
        except:
            pass
        time.sleep(30)

if __name__ == "__main__":
    main()
