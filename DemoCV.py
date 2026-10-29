import base64
import math
import mimetypes
import os
import sys
from pathlib import Path

from openai import OpenAI, OpenAIError
from PyQt6.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QResizeEvent
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VISION_MODEL = "gpt-4.1-mini"
EMBEDDING_MODEL = "text-embedding-3-small"


def load_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return api_key

    env_path = Path(__file__).resolve().with_name(".env")
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith("#") or "=" not in stripped_line:
                continue
            name, value = stripped_line.split("=", 1)
            if name.strip() == "OPENAI_API_KEY":
                api_key = value.strip().strip("\"'")
                if api_key:
                    return api_key

    raise RuntimeError(
        "OPENAI_API_KEY를 환경 변수 또는 DemoCV.py와 같은 폴더의 .env 파일에 설정하세요."
    )


def encode_image(image_path: Path) -> tuple[str, str]:
    mime_type, _ = mimetypes.guess_type(image_path.name)
    if mime_type not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
        raise ValueError(f"지원하지 않는 이미지 형식입니다: {image_path.name}")

    try:
        image_bytes = image_path.read_bytes()
    except OSError as exc:
        raise OSError(f"{image_path.name} 파일을 읽을 수 없습니다: {exc}") from exc
    image_data = base64.b64encode(image_bytes).decode("ascii")
    return mime_type, image_data


def describe_image(client: OpenAI, image_path: Path) -> str:
    mime_type, image_data = encode_image(image_path)
    response = client.responses.create(
        model=VISION_MODEL,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "사진에 보이는 주요 피사체, 색상, 배경, 장면을 "
                            "검색과 유사도 비교에 유용하도록 한국어로 간결하게 설명하세요."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime_type};base64,{image_data}",
                    },
                ],
            }
        ],
        max_output_tokens=250,
    )
    description = response.output_text.strip()
    if not description:
        raise ValueError(f"이미지 설명을 받지 못했습니다: {image_path.name}")
    return description


def cosine_similarity(first: list[float], second: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(first, second))
    first_norm = math.sqrt(sum(value * value for value in first))
    second_norm = math.sqrt(sum(value * value for value in second))
    if first_norm == 0 or second_norm == 0:
        return 0.0
    return dot_product / (first_norm * second_norm)


class ImageSearchWorker(QThread):
    progress = pyqtSignal(str)
    completed = pyqtSignal(str, object)
    failed = pyqtSignal(str)

    def __init__(self, source_path: Path, folder_path: Path) -> None:
        super().__init__()
        self.source_path = source_path
        self.folder_path = folder_path

    def run(self) -> None:
        try:
            client = OpenAI(api_key=load_api_key())
            self.progress.emit("선택한 사진을 분석하고 있습니다...")
            source_description = describe_image(client, self.source_path)

            source_resolved = self.source_path.resolve()
            image_paths = sorted(
                path
                for path in self.folder_path.rglob("*")
                if path.is_file()
                and path.suffix.lower() in SUPPORTED_EXTENSIONS
                and path.resolve() != source_resolved
            )
            if not image_paths:
                raise ValueError("선택한 폴더에 비교할 이미지가 없습니다.")

            descriptions: list[str] = []
            valid_paths: list[Path] = []
            for index, image_path in enumerate(image_paths, start=1):
                self.progress.emit(
                    f"비슷한 사진 분석 중... ({index}/{len(image_paths)}) "
                    f"{image_path.name}"
                )
                descriptions.append(describe_image(client, image_path))
                valid_paths.append(image_path)

            if not valid_paths:
                raise ValueError("폴더에서 읽을 수 있는 비교 이미지가 없습니다.")

            self.progress.emit("사진 설명의 유사도를 계산하고 있습니다...")
            embedding_response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=[source_description, *descriptions],
            )
            vectors = [item.embedding for item in embedding_response.data]
            if len(vectors) != len(valid_paths) + 1:
                raise ValueError("유사도 계산에 필요한 임베딩 결과가 충분하지 않습니다.")
            source_vector = vectors[0]
            matches = [
                (
                    str(image_path),
                    description,
                    cosine_similarity(source_vector, vector),
                )
                for image_path, description, vector in zip(
                    valid_paths, descriptions, vectors[1:]
                )
            ]
            matches.sort(key=lambda result: result[2], reverse=True)
            self.completed.emit(source_description, matches[:5])
        except (OpenAIError, OSError, RuntimeError, ValueError) as exc:
            self.failed.emit(str(exc))


class Form(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.source_path: Path | None = None
        self.folder_path: Path | None = None
        self.worker: ImageSearchWorker | None = None

        self.setWindowTitle("사진 분석 및 유사 이미지 찾기")
        self.resize(1000, 760)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.preview_label = QLabel("분석할 사진을 선택하세요.")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(320, 240)
        self.preview_label.setStyleSheet("border: 1px solid #999;")
        main_layout.addWidget(self.preview_label)

        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("분석할 사진 선택")
        self.upload_button.clicked.connect(self.select_source_image)
        button_layout.addWidget(self.upload_button)

        self.folder_button = QPushButton("비교할 사진 폴더 선택")
        self.folder_button.clicked.connect(self.select_image_folder)
        button_layout.addWidget(self.folder_button)

        self.search_button = QPushButton("분석 및 유사 사진 찾기")
        self.search_button.setEnabled(False)
        self.search_button.clicked.connect(self.start_search)
        button_layout.addWidget(self.search_button)
        main_layout.addLayout(button_layout)

        self.selection_label = QLabel("사진과 비교 폴더를 선택하세요.")
        main_layout.addWidget(self.selection_label)
        main_layout.addWidget(
            QLabel(
                "선택한 사진과 폴더의 이미지는 분석을 위해 OpenAI API로 전송됩니다."
            )
        )

        main_layout.addWidget(QLabel("사진 분석 결과"))
        self.description_edit = QTextEdit()
        self.description_edit.setReadOnly(True)
        self.description_edit.setMaximumHeight(120)
        main_layout.addWidget(self.description_edit)

        main_layout.addWidget(QLabel("유사한 사진 (최대 5장)"))
        self.results_list = QListWidget()
        self.results_list.setIconSize(QSize(120, 90))
        main_layout.addWidget(self.results_list, stretch=1)

        self.status_label = QLabel("준비")
        main_layout.addWidget(self.status_label)

    def select_source_image(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "분석할 사진 선택",
            "",
            "Images (*.jpg *.jpeg *.png *.webp *.gif)",
        )
        if not file_name:
            return

        self.source_path = Path(file_name)
        pixmap = QPixmap(file_name)
        if pixmap.isNull():
            QMessageBox.warning(self, "이미지 오류", "선택한 사진을 열 수 없습니다.")
            self.source_path = None
            return

        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.update_selection_label()

    def select_image_folder(self) -> None:
        folder_name = QFileDialog.getExistingDirectory(
            self, "비교할 사진이 있는 폴더 선택"
        )
        if not folder_name:
            return

        self.folder_path = Path(folder_name)
        self.update_selection_label()

    def update_selection_label(self) -> None:
        source_name = self.source_path.name if self.source_path else "선택 안 됨"
        folder_name = str(self.folder_path) if self.folder_path else "선택 안 됨"
        self.selection_label.setText(
            f"분석 사진: {source_name} | 비교 폴더: {folder_name}"
        )
        self.search_button.setEnabled(
            self.source_path is not None and self.folder_path is not None
        )

    def start_search(self) -> None:
        if self.source_path is None or self.folder_path is None:
            return

        self.results_list.clear()
        self.description_edit.clear()
        self.set_busy(True)
        self.status_label.setText("OpenAI API에 연결하고 있습니다...")

        self.worker = ImageSearchWorker(self.source_path, self.folder_path)
        self.worker.progress.connect(self.status_label.setText)
        self.worker.completed.connect(self.show_results)
        self.worker.failed.connect(self.show_error)
        self.worker.finished.connect(self.search_finished)
        self.worker.start()

    def show_results(
        self, description: str, matches: list[tuple[str, str, float]]
    ) -> None:
        self.description_edit.setPlainText(description)
        for image_name, image_description, similarity in matches:
            image_path = Path(image_name)
            item = QListWidgetItem(
                f"{image_path.name}  |  유사도 점수 {similarity:.3f}\n"
                f"{image_description}"
            )
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                thumbnail = pixmap.scaled(
                    120,
                    90,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                item.setIcon(QIcon(thumbnail))
            self.results_list.addItem(item)

        self.status_label.setText(f"유사한 사진 {self.results_list.count()}장을 찾았습니다.")

    def show_error(self, message: str) -> None:
        self.status_label.setText("분석을 완료하지 못했습니다.")
        QMessageBox.warning(self, "분석 오류", message)

    def set_busy(self, busy: bool) -> None:
        self.upload_button.setEnabled(not busy)
        self.folder_button.setEnabled(not busy)
        self.search_button.setEnabled(not busy)

    def search_finished(self) -> None:
        self.set_busy(False)
        self.update_selection_label()
        self.worker = None

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self.source_path is None:
            return
        pixmap = QPixmap(str(self.source_path))
        if not pixmap.isNull():
            self.preview_label.setPixmap(
                pixmap.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Form()
    window.show()
    sys.exit(app.exec())
