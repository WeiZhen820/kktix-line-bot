# 📁 main.py（使用 requests 模擬瀏覽器，繞過 Cloudflare）
import certifi
import os
import requests
from flask import Flask

app = Flask(__name__)

LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_GROUP_ID = os.getenv("LINE_GROUP_ID")
KKTIX_URL = os.getenv("KKTIX_URL")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "referer": "https://kktix.com/events/t982878a/registrations/new",
    "cookie": "_cfuvid=OhK3nL36bK0y.rjjvj9xnihnnMJZueNGvsI8_IQDc5I-1749178810827-0.0.1.1-604800000; _fbp=fb.1.1749178811466.182955887576342552; _hjSession_1979059=eyJpZCI6ImZjZDY0YzY2LTU4OTUtNGQyNS05OWI4LTgwNWMzNDJkZjcwMCIsImMiOjE3NDkxNzg4MTE1MjYsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=; _clck=117lx8d%7C2%7Cfwj%7C0%7C1983; _gid=GA1.2.1868892389.1749178812; _hjSessionUser_1979059=eyJpZCI6ImZkYTZjODAxLTJlYWItNTViYS1hYzYxLTk1YTQxODQyNzg4OCIsImNyZWF0ZWQiOjE3NDkxNzg4MTE1MjUsImV4aXN0aW5nIjp0cnVlfQ==; _dc_gtm_UA-44784359-1=1; _dc_gtm_null=1; cf_clearance=LJStnxjOCQ748Afg4cwGq9tZ0hDkDnjNrEmlFSq2YLI-1749179311-1.2.1.1-OX6iv5YzV1i9b.pO01zcA7412H1NGYR6MJu_YJp_CLl0T8Lfq1LBeRsZd2qdE3HlpQj4PGprVGfvxi182Vuxb9hmwyGz.Qh9I_HAn.qZh5vJQe.4jPBkUrXiZIrU7Vh5smdhoCxBWA.0GopCYSdM9SQuV8YMksEmM4_NmZFMgO7KnJk79n1hBi4ldaAY8vrUjsx9ONI1B9V3Dus8lYfXDiETBuFRrPjqT9a1VQjcZHnQOe1uw9A3WVOWlMVXzGEx9ouRfOL4DEPLyPI8KlDC.qDdg_RjMAFxj5IORyk0PQgFEgZRWswQr_2s2TkY.taDgssNEeZrsBWiQAfvI83yXQd0kqJaLEKI5xHwTDh1BvC7kzXqYjgbHMv4L0E.BHpX; user_display_name_v2=qqq_1234; user_avatar_url_v2=https%3A%2F%2Fwww.gravatar.com%2Favatar%2F2684977e9bffa3598c1fd7cba9bcf52e.png; user_id_v2=7404181; user_path_v2=%2Fuser%2F7404181; user_time_zone_v2=Asia%2FTaipei; user_time_zone_offset_v2=28800; personalInfoNotFinished=0; kktix_session_token_v2=057a9dff174f8c88df86429f3a94a29f; _ga=GA1.2.1969512822.1749178811; _clsk=1ghhufu%7C1749179312596%7C4%7C0%7Cb.clarity.ms%2Fcollect; _ga_WZBYP4N1ZG=GS2.2.s1749178812$o1$g1$t1749179312$j49$l0$h0; _gali=registrationsNewApp; XSRF-TOKEN=GJTSC0fSLNw%2FarSAR22nX0iZ90mqgMW98G5gWPkrWn4MLWRHcQsHaJW26PSEIgNWVt5tfempYY9dQDOET%2FkFlA%3D%3D; __cfwaitingroom=ChhpZ2VQM21heW9naExlVE1wNldWcm9RPT0SkAJabDZCUW9qQnZzWjhjYVk4d3BUS0FYdE1jcUZkL2VraGVRRm9ZZEhyTFBTQU50SEJBS3dNZWNPRENIbFFJbEltS0hEWVE1WUdDZjgvdEl4bFFkUFdUaVA2UlR5SDZhOFVmTUtzWDlkNUZFOG1VWEdxUVBDM2M0a1dPNnJnMWVIelY5ZjNtUEg4eTBFMUFKOUtQQ3BIbStvdWxJY29RNlZBRVdCR0lTaUtibnVYeXAweElGd1UrWGRHVjdCaHVlY08wSzBvWGV6SzVVUCtWSXRwazRCV0JOb1FQVDJGVEp6d1JhTWlmeUlnckU2czRYV09xaWdpMkhpVUZxQ2lMU2U5ODZuV0tKOFJLenpSU0t1bA%3D%3D; _ga_LWVPBSFGF6=GS2.1.s1749178811$o1$g1$t1749179328$j32$l0$h0; _ga_SYRTJY65JB=GS2.1.s1749178690$o14$g1$t1749179328$j32$l0$h0"
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


def check_kktix():
    print("🔁 check_kktix triggered")
    try:
        response = requests.get(KKTIX_URL, headers=headers, verify=certifi.where())
        print(response.text[:1000])  # debug: 印出前段 HTML 內容

        if "已售完" not in response.text:
            send_line_notify(f"🎟️ 有票啦！\n{KKTIX_URL}")
        else:
            print("❌ 目前全部已售完")
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
