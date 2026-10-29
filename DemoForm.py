#DemoForm.py
#Demoform.ui + DemoForm.py

import sys
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6 import uic 

#디자인 파일 로딩
form_class = uic.loadUiType("DemoForm.ui")[0]

#DemoForm 클래스 정의
class DemoForm(QDialog, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self) #화면단과 로직단 연결
        self.label.setText("Hello PyQt6") #화면단의 label에 텍스트 설정

#진입점 체크 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = DemoForm()
    demo.show()
    sys.exit(app.exec())