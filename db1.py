#db1.py
import sqlite3
#import pandas as pd

#df=pd.read_csv('C:/Users/student/Downloads/phonebook.csv')  
#save to memory permenently
conn = sqlite3.connect(r'c:\work\sample.db')
#create cursor object
cur = conn.cursor()
#create table
cur.execute('create table PhoneBook(name text, phone text);')
#insert data
cur.execute("insert into PhoneBook (name, phone) values(?,?);", ('Hong', '010-1234-1234'))
#multiple insert
datalist = [('Kim', '010-2345-2345'), ('Lee', '010-3456-3456'), ('Park', '010-4567-4567'), ('Choi', '010-5678-5678')]
cur.executemany("insert into PhoneBook (name, phone) values(?,?);", datalist)

cur.execute('select * from  PhoneBook;')
# for row in cur:
#     print(row)

print('---fetchone()---')
print(cur.fetchone())   
print('---fetchmany()---')
print(cur.fetchmany(2)) 
print('---fetchall()---') #2rows left
print(cur.fetchall())   
#fetchall() returns empty list, fill up
cur.execute('select * from  PhoneBook;')
print('---fetchall()---')
print(cur.fetchall())

conn.commit()
conn.close()
