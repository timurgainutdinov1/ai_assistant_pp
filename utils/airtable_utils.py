import logging
from typing import Any, Dict

import streamlit as st
from pyairtable import Api


class AirtableHandler:
    """
    Класс для работы с Airtable.
    """

    def __init__(self):
        """
        Инициализирует подключение к Airtable, используя секреты Streamlit.
        """
        self.api_key = st.secrets["AIRTABLE_API_KEY"]
        self.base_id = st.secrets["AIRTABLE_BASE_ID"]
        self.table_name = st.secrets["AIRTABLE_TABLE_NAME"]
        self.api = Api(self.api_key)
        self.table = self.api.table(self.base_id, self.table_name)
        self.record_id = None

    def save_to_airtable(self, results_json: Dict[str, Any]) -> None:
        """
        Сохраняет результаты проверки в Airtable.

        Args:
            results_json: Результаты проверки
        """
        # Подготавливаем данные для Airtable
        record = {
            "Имена загруженных файлов": ", ".join(results_json["inputs"]["names"]),
            "Содержимое паспорта": results_json["inputs"]["content"]["passport"],
            "Содержимое отчета": results_json["inputs"]["content"]["report"],
            "Входные критерии": results_json["inputs"]["content"]["criteria"],
            "Адаптированные критерии": results_json["outputs"]["content"][
                "check_criteria"
            ],
            "Оценка пользователя": results_json["feedback_from_user"].get("rating", ""),
            "Комментарий пользователя": results_json["feedback_from_user"].get(
                "comment", ""
            ),
            "Модель": results_json["llm"],
            "Результаты проверки": results_json["outputs"]["content"]["check_results"],
            "Обратная связь для студента": results_json["outputs"]["content"][
                "feedback_for_student"
            ],
            "Длительность проверки": results_json["duration"],
            "Длительность адаптации критериев": results_json["structuring_criteria_duration"],
            "Длительность проверки отчета": results_json["checking_report_duration"],
            "Длительность формирования обратной связи": results_json["feedback_forming_duration"],
            "Идентификатор сессии": results_json["session_id"],
        }
        try:
            self.record_id = self.table.create(record)["id"]
        except Exception as e:
            logging.error(f"Ошибка при сохранении в Airtable: {e}")

    def update_airtable(self, results_json: Dict[str, Any]) -> None:
        """
        Обновляет существующую запись в Airtable.

        Args:
            results_json: Результаты проверки
        """
        updated_record = {
            "Оценка пользователя": results_json["feedback_from_user"].get("rating", ""),
            "Комментарий пользователя": results_json["feedback_from_user"].get(
                "comment", ""
            ),
        }
        try:
            self.table.update(self.record_id, updated_record)
        except Exception as e:
            logging.error(f"Ошибка при обновлении в Airtable: {e}")
