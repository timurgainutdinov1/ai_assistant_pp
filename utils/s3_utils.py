import json
from typing import Dict

import s3fs
import streamlit as st

from utils.prompt_manager import prompt_manager


class S3Handler:
    """
    Класс для работы с S3.
    """

    def __init__(self):
        self.fs = s3fs.S3FileSystem(
            key=st.secrets["AWS_ACCESS_KEY_ID"],
            secret=st.secrets["AWS_SECRET_ACCESS_KEY"],
            endpoint_url=st.secrets["AWS_ENDPOINT_URL"],
        )
        self.bucket = st.secrets["AWS_BUCKET_NAME"]
        self.base_path = None

    def set_base_path(self, path: str) -> None:
        """
        Устанавливает base_path для последующих операций сохранения.

        Args:
            path: Путь в S3
        """
        self.base_path = f"{self.bucket}/{path}"

    def log_check_run(self, file_name: str, timestamp: str) -> None:
        """
        Записывает каждый успешный запуск проверки в файл 'logs.txt'
        с указанием текущего времени и имени файла отчета.

        Args:
            file_name: Имя проверяемого файла отчета
        """
        
        log_entry = f"{timestamp} - {file_name}\n"
        log_file_path = f"{self.bucket}/logs.txt"
        
        # Создаем файл, если он не существует
        # if not self.fs.exists(log_file_path):
        #     with self.fs.open(log_file_path, "w", encoding="utf-8") as f:
        #         f.write("")
                
        with self.fs.open(log_file_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def _save_file(self, file_path: str, content: bytes) -> None:
        """Вспомогательный метод для сохранения одного файла в S3"""
        with self.fs.open(file_path, "wb") as f:
            f.write(content)

    def save_files_to_s3(
        self,
        files: Dict[str, bytes],
    ) -> None:
        """
        Сохраняет документы в S3.

        Args:
            files: Словарь с файлами для сохранения
        """
        for file_type, content in files.items():
            if content:
                file_path = f"{self.base_path}/{file_type}"
                self._save_file(file_path, content)

    def save_results_json_to_s3(self, results_json: Dict) -> None:
        """
        Сохраняет все результаты в S3 в виде json.

        Args:
            results_json: Результаты проверки
        """
        # Добавляем тексты промптов и флаг модификации промптов
        results_json["prompts"] = {
            "custom_use": bool(prompt_manager.modified_prompts),
            "criteria_forming": prompt_manager.get_prompt("CRITERIA_FORMING_TEMPLATE"),
            "check_report": prompt_manager.get_prompt("CHECK_REPORT_TEMPLATE"),
            "feedback_forming": prompt_manager.get_prompt("FEEDBACK_FORMING_TEMPLATE"),
        }
        results_json_path = f"{self.base_path}/results.json"
        with self.fs.open(results_json_path, "w", encoding="utf-8") as f:
            json.dump(results_json, f, ensure_ascii=False, indent=4)



def save_to_s3(s3_handler, files_to_s3_save, report_file_name, results_json, timestamp):
    """
    Cохранение файлов в S3.

    Args:
        s3_handler: Объект для работы с S3
        files_to_s3_save: Словарь с файлами для сохранения
        report_file_name: Имя файла отчета
        results_json: JSON с результатами проверки
    """
    s3_handler.log_check_run(report_file_name, timestamp)
    s3_handler.save_files_to_s3(files_to_s3_save)
    s3_handler.save_results_json_to_s3(results_json)


def prepare_s3_files(files_to_save, check_result, check_criteria, feedback):
    """
    Подготавливает файлы для сохранения в S3.

    Args:
        files_to_save: Словарь с исходными файлами
        check_result: Результаты проверки
        check_criteria: Структурированные критерии оценки
        feedback: Обратная связь для студента

    Returns:
        Dict[str, bytes]: Словарь с подготовленными файлами для сохранения в S3
    """
    files_to_s3_save = {}
    # Получаем исходные файлы
    for file in files_to_save.values():
        if file:
            files_to_s3_save[file.name] = file.getvalue()

    # Добавляем результаты проверки и критерии
    files_to_s3_save["Результаты проверки.md"] = check_result.encode()
    files_to_s3_save["Адаптированные критерии проверки.md"] = check_criteria.encode()

    # Добавляем обратную связь, если она была сгенерирована
    if feedback:
        files_to_s3_save["Обратная связь для студента.md"] = feedback.encode()
        
    return files_to_s3_save