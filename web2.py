#web2.py
#webcrawler for clien.net
from bs4 import BeautifulSoup
import urllib.request 
import re

#save to file(wt: write text)
f = open('clien.txt', 'wt', encoding='utf-8')
hdr = {'User-Agent': 'Mozilla/5.0'}

for i in range(0, 10):

    url = 'https://www.clien.net/service/board/sold?&od=T31&category=0&po=' + str(i)
    # https://www.clien.net/service/board/sold
    # https://www.clien.net/service/board/sold?&od=T31&category=0&po=1

    #요청객체 생성
    req = urllib.request.Request(url, headers=hdr)
    page = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(page, 'html.parser')

    #매물 정보 추출
    items = soup.find_all('span', attrs={'data-role': 'list-title-text'})
    for item in items:
        title = item.text.strip()
        if re.search('애플워치', title): #문자열에 '아이폰' 포함되면
            print('page', i, '.', title)    
            f.write(title + '\n')

    #close the file
f.close()

# <span class="subject_fixed" data-role="list-title-text" title="[택포 1만] 상도전기 차단기 분전반커버">
# 							[택포 1만] 상도전기 차단기 분전반커버
# 						</span>