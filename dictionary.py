#dictionary
d = {'apple':'red', 'banana':'yellow'}
print(len(d))
print(d['apple'])
d['kiwi'] = 'green' 
d['apple'] = 'yellow'
print(d)
del d['apple']
print(d)
for item in d.items():
    print(item)


#boolean
isRight = True
print(type(isRight))
print(1<2)
print(1>2)
x=5
y=6
print(x==y)
print(x!=y)
print(not isRight)
print(True and True and True)
print(True and True and False)
print(True or False or False)


