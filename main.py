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
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "referer": KKTIX_EVENT_URL,
    "Cookie": "_fbp=fb.1.1748144778833.551661953454308993; locale=zh-TW; _hjSessionUser_1979059=eyJpZCI6IjUyNjRiZmRiLWJjODYtNTY2MS04ZmJlLTNmZDg3Yjc5YjNkYSIsImNyZWF0ZWQiOjE3NDgxNDQ3Nzg4NjAsImV4aXN0aW5nIjp0cnVlfQ==; _cfuvid=HdhtPCuXefspbhLdHZxCV6UNg2Vo9bpemGm.jO9LZnQ-1749215755205-0.0.1.1-604800000; _hjSession_1979059=eyJpZCI6IjIwMzJhZTRiLTkzYjgtNDFlZC1iN2JiLTg1NDM5MWM5ZDcxMyIsImMiOjE3NDkyMTU3NTAyMTYsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MX0=; _gid=GA1.2.407508483.1749215750; _clck=11p6rgg%7C2%7Cfwj%7C0%7C1971; _ga_FY1FJ045WS=GS2.1.s1749217603$o1$g1$t1749217607$j56$l0$h0; _dc_gtm_UA-44784359-1=1; cf_clearance=7EyOKQGrf6cH7BQxQxtZ6BNXo_SQfrdHpLxnBaUk1hQ-1749221376-1.2.1.1-88HeU0CRhvG29HpyieAF_UtvuAyZkpUP3eR8N2LyC3zBp4ayEhl9OG0PsNYT2zkDgnVUMAoM37TfM2eZODlGQugp2lb81zkNTM5.C4XlrMgnVwNvwAJVH.BKDS5lH8myuyXOCbHk9jKl9h084Bu99f7bmA73ZgMaOnmUL7WueTVs13W2zoqM4Ujshw.kMGNSE_e56GWIDEn.dHWTBSo3oj4d4Ihp4p8qV49dBdKAVtfxss6.XffJEgWcjU5xa1QYBEUGSzl4LFG0ofpCu6axPYjRNPX9o7bsMJfZXRr3M8GDiOy64_3p.Tbj5obEM4xA5idRm.FczpB5bp7V4J8q7sBD4bNoaMpF3cOid9FOwXhRdgsmzneiGxb9rJEfmo6W; user_display_name_v2=zhen_820; user_avatar_url_v2=https%3A%2F%2Fwww.gravatar.com%2Favatar%2Fb82021ea42bc34e05128f622dd698f60.png; user_id_v2=5189000; user_path_v2=%2Fuser%2F5189000; user_time_zone_v2=Asia%2FTaipei; user_time_zone_offset_v2=28800; personalInfoNotFinished=0; kktix_session_token_v2=7ba53f09bb30d3b6aeed528e50dd30ad; mobileNotVerified=0; _ga=GA1.2.1402664097.1748144779; _dc_gtm_null=1; _ga_WZBYP4N1ZG=GS2.2.s1749221352$o3$g1$t1749221399$j13$l0$h0; _clsk=a6z426%7C1749221400064%7C7%7C0%7Ch.clarity.ms%2Fcollect; XSRF-TOKEN=vHg2D2hvxuXwqYlLulJ4uEkyMu4zixs8ycsZV9h2YPTMr%2BiMNhCCR8OKh7zf67E%2FH%2B0oYdLNRJqJtJ3IV93lqQ%3D%3D; __cfwaitingroom=ChhLNTQxaTdVRk96MkhzMnMvb0trR0RnPT0SkAJEVy9aeFc3bHl1djh3TUQweU1PeHpvZ1lYZXhyTkRPZ1R5ZkRqNmU1a2JoMVBHQUlFalNMT3ZjOWY5Vmp4VkJYVGZJSVhpTUJqM0ZxaXFWL3BuYnpDbGpQT3ZNTDVZckRmczJhaHVsWGVNemRlbkVIOWdJbVBkVXJnMzBHam5wTjRjNEMyS1VLbzRMa3lhVzBYdWVvREt2aFNRZDhRNFJaWXUwZDdoTGxWRHVCWmxwZWhqTmlmSWM2TStGaVREaHJhaEI1Y3o2OXptUEJzR0ZyOU4rZWprbWlwTEE1SXZSOWJqTkpXQzNtUG1XaGdYZVpCSm5RKzlkazE5aTE1bnEwZlRFdVRNdGQ1UmlYMktlNg%3D%3D; _ga_LWVPBSFGF6=GS2.1.s1749215750$o2$g1$t1749221404$j7$l0$h0; _ga_SYRTJY65JB=GS2.1.s1749215750$o2$g1$t1749221404$j7$l0$h0",
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
        print("回傳狀態碼:", res.status_code)
        print("前 100 字:", res.text[:100])
        if not res.text.strip().startswith("{"):
            print("⚠️ 回傳不是 JSON，可能是 HTML 錯誤頁")
            return
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
