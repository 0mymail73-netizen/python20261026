#DemoForm2.py
#Demoform2.ui + DemoForm.py

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic 
from bs4 import BeautifulSoup
import urllib.request 
import re

#디자인 파일 로딩
form_class = uic.loadUiType("DemoForm2.ui")[0]

#DemoForm 클래스 정의(상속받는 부모 클래스를 QMainWindow로 변경)
class DemoForm(QMainWindow, form_class):
    def firstClick(self):
        self.label.setText('1st button clicked')
    def secondClick(self):
        self.label.setText('2nd button clicked')
    def thirdClick(self):
        self.label.setText('3rd button clicked')

#진입점 체크 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = DemoForm()
    demo.show()
    sys.exit(app.exec())