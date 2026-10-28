from pathlib import Path
import shutil


DOWNLOADS_DIR = Path(r"C:\Users\student\Downloads")

FILE_CATEGORIES = {
    "images": {".jpg", ".jpeg"},
    "data": {".csv", ".xlsx"},
    "docs": {".txt", ".doc", ".pdf"},
    "archive": {".zip"},
}


def organize_downloads(downloads_dir: Path = DOWNLOADS_DIR) -> None:
    for folder_name in FILE_CATEGORIES:
        (downloads_dir / folder_name).mkdir(parents=True, exist_ok=True)

    for source in downloads_dir.iterdir():
        if not source.is_file():
            continue

        extension = source.suffix.lower()
        destination_folder = next(
            (
                folder_name
                for folder_name, extensions in FILE_CATEGORIES.items()
                if extension in extensions
            ),
            None,
        )
        if destination_folder is None:
            continue

        destination = downloads_dir / destination_folder / source.name
        if destination.exists():
            raise FileExistsError(f"Destination already exists: {destination}")

        shutil.move(str(source), str(destination))


if __name__ == "__main__":
    organize_downloads()
    print("다운로드 파일 정리를 완료했습니다.")
