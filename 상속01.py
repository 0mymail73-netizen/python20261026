#부모클래스 정의
class Person:
    def __init__(self, name, phoneNumber):
        self.name = name
        self.phoneNumber = phoneNumber

    def printInfo(self):
        print("Info(Name:{0}, Phone Number: {1})".format(self.name, self.phoneNumber))

#자식클래스 정의
class Student(Person):
    #override
    def __init__(self, name, phoneNumber, subject, studentID):
        #self.name = name
        #self.phoneNumber = phoneNumber
        super().__init__(name, phoneNumber)
        self.subject = subject
        self.studentID = studentID
        #printInfo 
    def printInfo(self):
        super().printInfo()
        print("Info(name:{0}, phone Number: {1}, subject: {2}, studentID: {3})"
              .format(self.name, self.phoneNumber, self.subject, self.studentID))



p = Person("전우치", "010-222-1234")
s = Student("이순신", "010-111-1234", "컴공", "991122")
print(p.__dict__)
print(s.__dict__)


