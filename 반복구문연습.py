#반복구문
value = 5
while value > 0:
    print(value)
    value -= 1

print('--- for in ---')
for i in range(value < 10):
    print(i)
    i += 1

print('---날짜, 연도 생성---')
print(list(range(2000, 2027)))
print(list(range(1,32)))

lst=list(range(1,11))
for item in lst:
    print(item)

#list comprehension
lst = list(range(1,11))
print([i**2 for i in lst if i>5])
words = ['apple', 'banana', 'cherry']
print([word.upper() for word in words])
    