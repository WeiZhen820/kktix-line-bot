# 📁 main.py（本機可測試，含票種偵測與 LINE 通知）

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from flask import Flask

app = Flask(__name__)

LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_GROUP_ID = os.getenv("LINE_GROUP_ID")
KKTIX_URL = os.getenv("KKTIX_URL")


def send_line_notify(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    body = {
        "to": LINE_GROUP_ID,
        "messages": [{"type": "text", "text": message}]
    }
    res = requests.post(url, headers=headers, json=body)
    print("LINE 回應:", res.text)


def check_kktix():
    print("🔁 check_kktix triggered")

    options = Options()
    # ⚠️ 若部署於 Render 請開啟 headless
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(KKTIX_URL)
        time.sleep(5)  # 確保 JS 資料載入完成

        # 印出 HTML 頁面開頭方便 debug
        print(driver.page_source[:1000])

        blocks = driver.find_elements(By.CSS_SELECTOR, ".ticket-type-row")
        found = False

        for block in blocks:
            try:
                name = block.find_element(By.CSS_SELECTOR, ".ticket-type-title").text
                price = block.find_element(By.CSS_SELECTOR, ".ticket-price").text
                sold_out = block.find_elements(By.XPATH, ".//*[contains(text(),'已售完')]")

                print(f"🧪 票種：{name} - {price} - Sold Out: {bool(sold_out)}")

                if not sold_out:
                    send_line_notify(f"🎟️ 有票：{name} - {price}\n{KKTIX_URL}")
                    found = True
            except Exception as e:
                print("❌ 票種讀取錯誤:", e)

        if not found:
            print("❌ 目前全部已售完")

    except Exception as e:
        print("❌ Selenium 錯誤:", e)
    finally:
        driver.quit()


@app.route("/")
def home():
    return "KKTIX LINE bot 正在執行中"


@app.route("/check")
def run_check():
    try:
        check_kktix()
        return "Checked", 200
    except Exception as e:
        return f"Error: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
