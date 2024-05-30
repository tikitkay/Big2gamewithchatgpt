import requests
import os

url = "https://www.deckofcardsapi.com/static/img/back.png"
response = requests.get(url)

os.makedirs('cards', exist_ok=True)

with open('cards/back.png', 'wb') as f:
    f.write(response.content)

print("카드 뒷면 이미지 다운로드 완료!")
