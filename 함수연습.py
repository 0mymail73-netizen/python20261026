#함수연습.py

#1)함수 정의
def times(a,b):
    return a+b, a*b

#2)call func
result = times(3,4)
print(result)

def setValue(newValue):
    x = newValue
    print('local Variable: ', x)

result = setValue(5)
print(result)

#함수내부 이름해석 LEGB
x = 10
def func(a):
    return a+x

def func2(a):
    x = 5
    return a + x

print(func2(1))

#기본값 명시
def times(a=10, b=20):
    return a*b

#호출
print(times())
print(times(5))
print(times(5,6))

#키워드인자
def connectURI(server, port):
    return 'https://' + server + ':' + port

print(connectURI(server='localhost', port= '8080'))
print(connectURI(port='8080', server='localhost'))

#가변인자
def union(*ar):
    result = []
    for item in ar:
        for x in item:
            if x not in result:
                result.append(x)
    return result

#호출
print(union('HAM', 'EGG'))
print(union('HAM', 'EGG', 'SPAM'))

#LAMBDA
g = lambda x,y:x*y
print(g(3,4))
print((lambda x:x*x)(3))

print(dir())
print(globals())

#필터링
lst = [10, 25, 30]
iterL = filter(None, lst)
for item in iterL:
    print(item)

def getBiggerThan20(x):
    return x>20

print('---filtering function used---')
iterL = filter(getBiggerThan20, lst)
for item in iterL:
    print(item)

print('---filtering lambda used---')
iterL = filter(lambda x:x>20, lst)
for item in iterL:
    print(item)

#mapping function
for item in map(lambda x:x*2, lst):
    print(item)