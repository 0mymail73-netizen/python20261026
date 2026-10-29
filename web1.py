from bs4 import BeautifulSoup

#load the html file
page = open('chap09_test.html', 'rt', encoding='utf-8').read()

#easy to serarch and navigate the html file
soup = BeautifulSoup(page, 'html.parser')
#view all the html code in a readable format
# print(soup.prettify())
#find all the links in the html file
# print(soup.find_all('a'))
print(soup.find_all('p'))

#search for the first link in the html file
# print(soup.find('p'))

#conditional search for the links in the html file
# print(soup.find_all('p', class_='outer'))
#attributes can be used to search for specific attributes in the html file
# print(soup.find_all('p', attrs= {'class': 'outer'}))

#search for the string in the tag
for tag in soup.find_all('p'):
    title = tag.text.strip()
    title = title.replace('\n', '')
    print(title)

print('---문자열 처리 메서드---')
data = '<<< spam ham egg >>>'
result = data.strip('<>') #remove the characters in the string
print(data)
print(result)

result=result.replace('spam', '스팸') #replace the string with another string
print(result)

lst = result.split() #split the string into a list
print(lst)

result2 = ' '.join(lst) #join the list into a string
print(result2)

#regular expression
import re

result = re.search('[0-9]*th', '35th')
print(result)
print(result.group())#문자열만 보여줌

result = re.search('\d{4}', '올해는 2026년입이다.')
print(result)
print(result.group())
result = re.search('apple', 'this is apple')
print(result)
print(result.group())
