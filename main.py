import requests
from bs4 import BeautifulSoup
import json
import os
import sys

# Discord 설정
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1290546826159853629/S-cHyMvZW7y2l-v4UtzQ1tg5htnFD569FoH40E5blLRXqQl_ZWvBqJt67oFzJs__xOaU'  # 여기에 복사한 웹훅 URL을 입력하세요.

# 공지사항 URL 목록
urls = {
    'cau': 'https://www.cau.ac.kr/cms/FR_CON/index.do?MENU_ID=100&CONTENTS_NO=1&P_TAB_NO=1#page1',
    'kaist': 'https://gsai.kaist.ac.kr/notice/?lang=ko',
    'disu': 'https://www.disu.ac.kr/community/notice'
}

# 이전 공지사항을 저장할 파일 경로
DATA_FILE = 'notices.json'

def load_previous_notices():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_current_notices(notices):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(notices, f, ensure_ascii=False, indent=4)

def send_discord_message(message):
    data = {
        'content': message
    }
    response = requests.post(DISCORD_WEBHOOK_URL, data=data)
    if response.status_code != 204:
        print(f"Discord로 메시지 전송 실패: {response.status_code}")

def fetch_notices():
    notices = {}
    headers = {'User-Agent': 'Mozilla/5.0'}

    # 중앙대학교 공지사항 크롤링
    response = requests.get(urls['cau'], headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    cau_notices = soup.select('.board-list li .subject a')
    notices['cau'] = [notice.get_text(strip=True) for notice in cau_notices]

    # KAIST 공지사항 크롤링
    response = requests.get(urls['kaist'], headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    kaist_notices = soup.select('.board-list .title a')
    notices['kaist'] = [notice.get_text(strip=True) for notice in kaist_notices]

    # 동의과학대학교 공지사항 크롤링
    response = requests.get(urls['disu'], headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    disu_notices = soup.select('.bbs_list tbody tr .subject a')
    notices['disu'] = [notice.get_text(strip=True) for notice in disu_notices]

    return notices

def compare_notices(old, new):
    updates = {}
    for key in new:
        if key in old:
            diff = [item for item in new[key] if item not in old[key]]
            if diff:
                updates[key] = diff
        else:
            updates[key] = new[key]
    return updates

def main():
    old_notices = load_previous_notices()
    current_notices = fetch_notices()
    updates = compare_notices(old_notices, current_notices)

    for site, new_items in updates.items():
        for item in new_items:
            message = f"[{site.upper()} 새 공지사항]\n{item}"
            send_discord_message(message)

    save_current_notices(current_notices)


"""def main():
    TEST_MODE = False
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        TEST_MODE = True

    old_notices = load_previous_notices()
    current_notices = fetch_notices()

    if TEST_MODE:
        # 가짜 공지사항 추가
        for key in current_notices:
            current_notices[key].insert(0, '테스트 공지사항 - 이건 가짜 공지입니다.')

    updates = compare_notices(old_notices, current_notices)

    for site, new_items in updates.items():
        for item in new_items:
            message = f"[{site.upper()} 새 공지사항]\n{item}"
            send_discord_message(message)

    save_current_notices(current_notices)"""

if __name__ == '__main__':
    main()
