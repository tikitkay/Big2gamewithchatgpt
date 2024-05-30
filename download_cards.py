import os
import requests

# 카드 이미지 URL 패턴
base_url = "https://deckofcardsapi.com/static/img/"
suits = ['D', 'C', 'H', 'S']
ranks = ['3', '4', '5', '6', '7', '8', '9', '0', 'J', 'Q', 'K', 'A', '2']

# cards 폴더 생성
if not os.path.exists('cards'):
    os.makedirs('cards')

# 각 카드 이미지 다운로드
for suit in suits:
    for rank in ranks:
        file_name = f"{rank}_of_{suit.lower()}.png"
        url = f"{base_url}{rank}{suit}.png"
        response = requests.get(url)
        if response.status_code == 200:
            with open(os.path.join('cards', file_name), 'wb') as file:
                file.write(response.content)
            print(f"Downloaded {file_name}")
        else:
            print(f"Failed to download {file_name}")
