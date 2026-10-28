#클래스 연습

#1. define class
class Person:
    def __init__(self):
        self.name = 'default name'
    def printInfo(self):
        #기존방식
        print('my name is {0}'.format(self.name))
        #f-string
        print(f'My name is  {self.name}')

#2. create instance
p1 = Person()
p2 = Person()

#3. call method
p1.printInfo()
p2.printInfo()

