#web2.py
#webcrawler for clien.net
from bs4 import BeautifulSoup
import urllib.request 
import re

#save to file(wt: write text)
f = open('todayhumor.txt', 'wt', encoding='utf-8')
hdr = {'User-Agent': 'Mozilla/5.0'}

for i in range(1, 11):

    url = 'https://www.todayhumor.co.kr/board/list.php?table=bestofbest&page=' + str(i)
    # https://www.clien.net/service/board/sold
    # https://www.clien.net/service/board/sold?&od=T31&category=0&po=1
    print(url)
    #요청객체 생성
    req = urllib.request.Request(url, headers=hdr)
    page = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(page, 'html.parser')

    #게시글 정보 추출
    items = soup.find_all('td', attrs={'class': 'subject'})
    for item in items:
        title = item.find('a').text.strip()
        if re.search('한국', title):
            print('page', i, '.', title)
            f.write(title + '\n')

    #close the file
f.close()

# <td class="subject"><a href="/board/view.php?table=bestofbest&amp;no=484026&amp;s_no=484026&amp;page=2" target="_top">빌라로 숨어든 배달기사 뒤따라간 사장님이 본 것</a><span class="list_memo_count_span"> [13]</span>  <span style="margin-left:4px;"><img src="//www.todayhumor.co.kr/board/images/list_icon_photo.gif" style="vertical-align:middle; margin-bottom:1px;"> </span><img src="//www.todayhumor.co.kr/board/images/list_icon_shovel.gif?2" alt="펌글" style="margin-right:3px;top:2px;position:relative"> </td>
# <a href="/board/view.php?table=bestofbest&amp;no=484026&amp;s_no=484026&amp;page=2" target="_top">빌라로 숨어든 배달기사 뒤따라간 사장님이 본 것</a>