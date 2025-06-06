import os
import re
import json
import requests
import urllib3
from flask import Flask
from bs4 import BeautifulSoup

app = Flask(__name__)

LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_GROUP_ID = os.getenv("LINE_GROUP_ID")
KKTIX_EVENT_ID = os.getenv("KKTIX_EVENT_ID") or "t982878a"  # 可自訂
KKTIX_EVENT_URL = f"https://kktix.com/events/{KKTIX_EVENT_ID}/registrations/new"
KKTIX_INFO_URL = f"https://kktix.com/g/events/{KKTIX_EVENT_ID}/register_info"

headers = {
    "user-agent": "Mozilla/5.0",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "referer": KKTIX_EVENT_URL,
}

def send_line_notify(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers_line = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    body = {
        "to": LINE_GROUP_ID,
        "messages": [{"type": "text", "text": message}]
    }
    res = requests.post(url, headers=headers_line, json=body)
    print("LINE 回應:", res.text)


def fetch_ticket_id_name_map():
    try:
        res = requests.get(KKTIX_EVENT_URL, headers=headers, verify=False)
        soup = BeautifulSoup(res.text, "html.parser")
        ticket_map = {}

        for div in soup.select("div.display-table[id^='ticket_']"):
            m = re.match(r"ticket_(\d+)", div.get("id", ""))
            if not m:
                continue
            ticket_id = m.group(1)
            name_el = div.select_one(".ticket-name")
            if name_el:
                ticket_map[ticket_id] = name_el.get_text(strip=True)
        return ticket_map
    except Exception as e:
        print("❌ 無法解析票種名稱：", e)
        return {}

def check_kktix():
    print("🔁 check_kktix triggered")
    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        ticket_names = fetch_ticket_id_name_map()
        res = requests.get(KKTIX_INFO_URL, headers=headers, verify=False)
        data = res.json()

        if data.get("register_status") == "SOLD_OUT":
            print("❌ register_status 顯示已售完")
            return

        tickets = data.get("tickets", [])
        messages = []

        for t in tickets:
            if t.get("in_stock"):
                tid = str(t.get("id"))
                name = ticket_names.get(tid, f"票種 {tid}")
                messages.append(f"🎫 {name} 有票！")

        if messages:
            msg = f"🎟️ 有票啦！\n{KKTIX_EVENT_URL}\n\n" + "\n".join(messages)
            send_line_notify(msg)
        else:
            print("❌ 沒有任何票種顯示 in_stock=True")
    except Exception as e:
        print("❌ 錯誤：", e)


@app.route("/")
def home():
    return "KKTIX bot 正在執行中"


@app.route("/check")
def run_check():
    try:
        check_kktix()
        return "Checked", 200
    except Exception as e:
        return f"Error: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
