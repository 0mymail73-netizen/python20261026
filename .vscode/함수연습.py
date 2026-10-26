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
    X=5
    return a+x

print(func2(1))
