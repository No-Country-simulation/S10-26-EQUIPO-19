import time
import requests
from datetime import datetime

URL = "https://openbridge-rcv2.onrender.com/health"
INTERVAL = 10 * 60

while True:
    try:
        response = requests.get(URL, timeout=30)

        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] "
            f"Status: {response.status_code} - {response.text}"
        )

    except requests.RequestException as e:
        print(f"[{datetime.now()}] Error: {e}")

    time.sleep(INTERVAL)
