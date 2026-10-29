import sys
import sqlite3
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from BikeManager import BikeManager


class ProductWindow(QMainWindow):
    def __init__(self, database_path: Path | None = None) -> None:
        super().__init__()
        if database_path is None:
            database_path = Path(__file__).resolve().with_name("MyProduct.db")
        self.repository = BikeManager(database_path)
        self.setWindowTitle("자전거 용품 관리")
        self.resize(860, 680)
        self.setMinimumSize(720, 580)
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f2f6f4;
            }
            QWidget#centralWidget {
                background-color: #f2f6f4;
            }
            QWidget#heroCard {
                background-color: #153d35;
                border-radius: 16px;
            }
            QLabel#pageTitle {
                color: #ffffff;
                font-size: 25px;
                font-weight: 700;
            }
            QLabel#pageSubtitle {
                color: #c4ddd3;
                font-size: 13px;
            }
            QWidget#formCard, QWidget#listCard {
                background-color: #ffffff;
                border: 1px solid #e1eae5;
                border-radius: 14px;
            }
            QLabel#sectionTitle {
                color: #203b33;
                font-size: 16px;
                font-weight: 700;
                border: none;
            }
            QLabel#fieldLabel {
                color: #52665f;
                font-size: 13px;
                font-weight: 600;
                border: none;
            }
            QLineEdit {
                color: #263a33;
                background-color: #f8faf9;
                border: 1px solid #dce7e1;
                border-radius: 8px;
                padding: 9px 11px;
                selection-background-color: #25866b;
                min-height: 20px;
            }
            QLineEdit:focus {
                background-color: #ffffff;
                border: 1px solid #25866b;
            }
            QLineEdit:read-only {
                color: #71817b;
                background-color: #edf2ef;
            }
            QPushButton {
                color: #ffffff;
                background-color: #25866b;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 13px;
                font-weight: 700;
                min-width: 76px;
            }
            QPushButton:hover {
                background-color: #1d725a;
            }
            QPushButton:pressed {
                background-color: #165944;
            }
            QPushButton#updateButton {
                background-color: #3978a8;
            }
            QPushButton#updateButton:hover {
                background-color: #2e638d;
            }
            QPushButton#deleteButton {
                background-color: #d65b57;
            }
            QPushButton#deleteButton:hover {
                background-color: #bb4845;
            }
            QPushButton#searchButton {
                color: #285447;
                background-color: #e4f2eb;
                border: 1px solid #cce4d7;
            }
            QPushButton#searchButton:hover {
                background-color: #d4eade;
            }
            QTableWidget {
                color: #30443c;
                background-color: #ffffff;
                alternate-background-color: #f7faf8;
                border: 1px solid #e5ece8;
                border-radius: 8px;
                gridline-color: #edf1ef;
                selection-background-color: #dcefe5;
                selection-color: #174b3a;
                outline: none;
            }
            QHeaderView::section {
                color: #496258;
                background-color: #f1f6f3;
                border: none;
                border-bottom: 1px solid #dfe9e3;
                padding: 11px 8px;
                font-weight: 700;
            }
            QTableWidget::item {
                padding: 7px;
                border-bottom: 1px solid #f0f3f1;
            }
            QStatusBar {
                color: #52665f;
                background-color: #e8efeb;
                border-top: 1px solid #dce6e0;
            }
            """
        )
        self._setup_ui()
        self.load_products()

    def _setup_ui(self) -> None:
        central_widget = QWidget(self)
        central_widget.setObjectName("centralWidget")
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(26, 24, 26, 18)
        main_layout.setSpacing(16)

        hero_card = QWidget()
        hero_card.setObjectName("heroCard")
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(24, 19, 24, 20)
        hero_layout.setSpacing(5)
        title = QLabel("자전거 용품 관리")
        title.setObjectName("pageTitle")
        subtitle = QLabel("용품 정보를 간편하게 등록하고 관리하세요.")
        subtitle.setObjectName("pageSubtitle")
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        main_layout.addWidget(hero_card)

        form_card = QWidget()
        form_card.setObjectName("formCard")
        form_card_layout = QVBoxLayout(form_card)
        form_card_layout.setContentsMargins(20, 16, 20, 18)
        form_card_layout.setSpacing(12)
        form_title = QLabel("제품 정보")
        form_title.setObjectName("sectionTitle")
        form_card_layout.addWidget(form_title)
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(18)
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.id_input = QLineEdit()
        self.id_input.setReadOnly(True)
        self.id_input.setPlaceholderText("자동 생성")
        self.id_input.setObjectName("idInput")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("예: 자전거 헬멧")
        self.name_input.setObjectName("nameInput")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("가격(원)")
        self.price_input.setObjectName("priceInput")
        for label_text, field in (
            ("제품 ID", self.id_input),
            ("제품명", self.name_input),
            ("가격", self.price_input),
        ):
            label = QLabel(label_text)
            label.setObjectName("fieldLabel")
            form_layout.addRow(label, field)
        form_card_layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(9)
        self.add_button = QPushButton("입력")
        self.add_button.setObjectName("addButton")
        self.update_button = QPushButton("수정")
        self.update_button.setObjectName("updateButton")
        self.delete_button = QPushButton("삭제")
        self.delete_button.setObjectName("deleteButton")
        self.search_button = QPushButton("검색")
        self.search_button.setObjectName("searchButton")
        for button in (
            self.add_button,
            self.update_button,
            self.delete_button,
            self.search_button,
        ):
            button_layout.addWidget(button)
        button_layout.addStretch()
        form_card_layout.addLayout(button_layout)
        main_layout.addWidget(form_card)

        list_card = QWidget()
        list_card.setObjectName("listCard")
        list_layout = QVBoxLayout(list_card)
        list_layout.setContentsMargins(20, 16, 20, 20)
        list_layout.setSpacing(12)
        list_title = QLabel("등록된 용품")
        list_title.setObjectName("sectionTitle")
        list_layout.addWidget(list_title)
        self.table_widget = QTableWidget(0, 3)
        self.table_widget.setObjectName("productTable")
        self.table_widget.setHorizontalHeaderLabels(["ID", "제품명", "가격(원)"])
        self.table_widget.setAlternatingRowColors(True)
        vertical_header = self.table_widget.verticalHeader()
        if vertical_header is not None:
            vertical_header.setVisible(False)
        self.table_widget.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table_widget.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.table_widget.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        header = self.table_widget.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(
                0, QHeaderView.ResizeMode.ResizeToContents
            )
            header.setSectionResizeMode(
                2, QHeaderView.ResizeMode.ResizeToContents
            )
        list_layout.addWidget(self.table_widget)
        main_layout.addWidget(list_card, 1)
        self.setCentralWidget(central_widget)

        self.add_button.clicked.connect(self.add_product)
        self.update_button.clicked.connect(self.update_product)
        self.delete_button.clicked.connect(self.delete_product)
        self.search_button.clicked.connect(self.search_products)
        self.name_input.returnPressed.connect(self.search_products)
        self.table_widget.itemSelectionChanged.connect(
            self.load_selected_product
        )

    def _product_values(self) -> tuple[str, int] | None:
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip().replace(",", "")
        if not name:
            QMessageBox.warning(self, "입력 확인", "제품명을 입력하세요.")
            return None
        try:
            price = int(price_text)
        except ValueError:
            QMessageBox.warning(self, "입력 확인", "가격을 숫자로 입력하세요.")
            return None
        if price < 0:
            QMessageBox.warning(self, "입력 확인", "가격은 0 이상이어야 합니다.")
            return None
        return name, price

    def _selected_product_id(self) -> int | None:
        product_id = self.id_input.text().strip()
        if not product_id:
            QMessageBox.warning(self, "선택 확인", "목록에서 제품을 선택하세요.")
            return None
        return int(product_id)

    def add_product(self) -> None:
        values = self._product_values()
        if values is None:
            return
        try:
            self.repository.add_product(*values)
            self.load_products()
            self._clear_form()
            self.status_bar.showMessage("제품을 등록했습니다.", 3000)
        except sqlite3.Error as error:
            self._show_database_error(error)

    def update_product(self) -> None:
        product_id = self._selected_product_id()
        if product_id is None:
            return
        values = self._product_values()
        if values is None:
            return
        try:
            if self.repository.update_product(product_id, *values):
                self.load_products()
                self._clear_form()
                self.status_bar.showMessage("제품을 수정했습니다.", 3000)
            else:
                QMessageBox.information(self, "검색 결과", "제품을 찾을 수 없습니다.")
                self.load_products()
        except sqlite3.Error as error:
            self._show_database_error(error)

    def delete_product(self) -> None:
        product_id = self._selected_product_id()
        if product_id is None:
            return
        answer = QMessageBox.question(
            self,
            "삭제 확인",
            "선택한 제품을 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            if self.repository.delete_product(product_id):
                self.load_products()
                self._clear_form()
                self.status_bar.showMessage("제품을 삭제했습니다.", 3000)
            else:
                QMessageBox.information(self, "검색 결과", "제품을 찾을 수 없습니다.")
                self.load_products()
        except sqlite3.Error as error:
            self._show_database_error(error)

    def search_products(self) -> None:
        try:
            self._display_products(self.repository.search_products(
                self.name_input.text().strip()
            ))
        except sqlite3.Error as error:
            self._show_database_error(error)

    def load_products(self) -> None:
        try:
            self._display_products(self.repository.search_products())
        except sqlite3.Error as error:
            self._show_database_error(error)

    def _display_products(self, products: list[tuple[int, str, int]]) -> None:
        self.table_widget.setRowCount(len(products))
        for row, (product_id, name, price) in enumerate(products):
            id_item = QTableWidgetItem(str(product_id))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            name_item = QTableWidgetItem(name)
            price_item = QTableWidgetItem(f"{price:,}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table_widget.setItem(row, 0, id_item)
            self.table_widget.setItem(row, 1, name_item)
            self.table_widget.setItem(row, 2, price_item)
        self.status_bar.showMessage(f"총 {len(products)}개 제품")

    def load_selected_product(self) -> None:
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return
        row = self.table_widget.currentRow()
        if row < 0:
            return
        id_item = self.table_widget.item(row, 0)
        name_item = self.table_widget.item(row, 1)
        price_item = self.table_widget.item(row, 2)
        if id_item is None or name_item is None or price_item is None:
            return
        self.id_input.setText(id_item.text())
        self.name_input.setText(name_item.text())
        self.price_input.setText(price_item.text().replace(",", ""))

    def _clear_form(self) -> None:
        self.id_input.clear()
        self.name_input.clear()
        self.price_input.clear()
        self.table_widget.clearSelection()

    def _show_database_error(self, error: sqlite3.Error) -> None:
        QMessageBox.critical(
            self,
            "데이터베이스 오류",
            f"데이터베이스 작업에 실패했습니다.\n{error}",
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductWindow()
    window.show()
    sys.exit(app.exec())
