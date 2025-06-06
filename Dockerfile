FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安裝系統依賴與 Chrome
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg ca-certificates fonts-liberation libappindicator3-1 \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 \
    libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 xdg-utils libgbm1 libgtk-3-0 \
    chromium chromium-driver

# 設定 Chrome 路徑
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 建立應用目錄
WORKDIR /app
COPY . /app

# 安裝 Python 套件
RUN pip install --upgrade pip && pip install -r requirements.txt

# 預設執行
CMD ["python", "main.py"]
