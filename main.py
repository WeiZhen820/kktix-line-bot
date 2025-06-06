import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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
    print("LINE Response:", res.text)


def check_kktix():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(KKTIX_URL)
        time.sleep(5)
        blocks = driver.find_elements(By.CSS_SELECTOR, ".ticket-type-row")

        found = False
        for block in blocks:
            name = block.find_element(By.CSS_SELECTOR, ".ticket-type-title").text
            price = block.find_element(By.CSS_SELECTOR, ".ticket-price").text
            sold_out = block.find_elements(By.XPATH, ".//*[contains(text(),'\u5df2\u552e\u5b8c')]")

            if not sold_out:
                send_line_notify(f"\U0001F39F\ufe0f \u6709\u7968\uff01{name} - {price}\n{KKTIX_URL}")
                found = True

        if not found:
            print("\u274c 目前全部已售完")

    except Exception as e:
        print("\u26a0\ufe0f Error:", e)
    finally:
        driver.quit()


if __name__ == "__main__":
    check_kktix()
