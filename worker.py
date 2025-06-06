import requests

def main():
    try:
        res = requests.get("https://kktix-line-bot.onrender.com/check")
        print("✅ 執行成功:", res.status_code, res.text)
    except Exception as e:
        print("❌ 錯誤：", e)

if __name__ == "__main__":
    main()
