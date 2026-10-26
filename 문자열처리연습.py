#string.py

strA="""이 문자열은
다중 라인으로
저장되어 있습니다.
"""

strB = "python is very powerful"

#디버깅 중단점
print(strA)
print(strB)
print(len(strB))
print(strB[0])
print(strB[0:6])
print(strB[:6])
print(strB[-1])
print(strB[-3:])

#list
colors = ['red', 'blue', 'green']
print(len(colors))
print(colors[0])
colors.append('yellow')
print(colors)
colors.insert(1, 'black')
print(colors)

#delete
colors.remove('blue')
print(colors)
for item in colors:
    print(item)

#sorting
colors.extend(['white', 'pink', 'orange'])
colors.sort()
print(colors)
colors.reverse()
print(colors)

#room numbers and count
print(colors.index('white'))
print(colors.count('pink'))

#set
a={1,2,3,3}
b={3,4,4,5}
print(a)
print(len(a))
print(a.union(b))
print(a.intersection(b))
print(a.difference(b))
print(b.difference(a))

#tuples
tp = (100, 200, 300)
print(type(tp))
print(len(tp))
print(tp[0])
print(tp.index(300))
print(tp.count(300))

#define functions
def times(a,b):
    return a+b, a*b 

#call functions
result = times(3,4)
print(result)
print("id:%s, name:%s" % ('kim', '김유신'))

#튜플로 묶기
args = (5,6)
print(times(*args))

a={1,2,3}
b = list(a)
b.append(10)
print(b)
print(int('10') +1)