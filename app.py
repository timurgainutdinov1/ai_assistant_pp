import os
import uuid

import streamlit as st

from compile_graph import graph
from file_handler import extract_text_from_file
from prompt_manager import prompt_manager


def get_file_uploader(label, file_types):
    """
    Функция для загрузки файлов.

    Args:
        label (str): Метка для загрузчика файлов.
        file_types (list): Список допустимых типов файлов.

    Returns:
        file: Загруженный файл.
    """
    return st.file_uploader(label, type=file_types)


def check_file_uploads(passport, criteria):
    """
    Проверяет наличие файлов и выводит одно предупреждение,
    если что-то отсутствует.

    Args:
        passport (file): Файл паспорта проекта.
        criteria (file): Файл критериев проверки.
    """
    warnings = []
    if passport is None:
        warnings.append("паспорт проекта не загружен")
    if criteria is None:
        warnings.append("используются критерии проверки по умолчанию")
    if warnings:
        st.warning(f"Предупреждение: {', '.join(warnings)}.")


def save_file(file, name=None):
    """
    Сохраняет загруженный файл с уникальным идентификатором.

    Args:
        file (file): Загруженный файл.
        name (str, optional): Имя файла для сохранения.
                              Если не указано,
                              используется имя загруженного файла
                              с уникальным идентификатором.

    Returns:
        str: Имя сохраненного файла.
    """
    unique_id = str(uuid.uuid4())
    file_name = f"{unique_id}_{name if name else file.name}"
    with open(file_name, "wb") as f:
        f.write(file.getbuffer())
    return file_name


def delete_files(files):
    """
    Удаляет файлы после обработки.

    Args:
        files (list): Список файлов для удаления.
    """
    for file in files:
        if file:
            os.remove(file)


def select_llm():
    """
    Выбор LLM.

    Returns:
        str: Выбранная LLM.
    """
    return st.selectbox(
        "Выберите LLM:", [
            "DeepSeek R1",
            "DeepSeek Chat",
            "Gemini 2.0 Pro",
            "Gemma 3 27B",
            "Gemini 2.0 Flash",
            "Llama 3.3 70B Instruct",
            "Qwen 32B",
            "Qwen 2.5 72B",
            "Mistral Small 24B"
        ]
    )


def main():
    st.title("AI-ассистент куратора проектного практикума")

    # Add tabs for main functionality and prompt management
    tab1, tab2 = st.tabs(["Проверка проектов", "Управление промптами"])

    with tab1:
        # Загружаем критерии по умолчанию
        with open("Критерии.txt", "r", encoding="utf-8") as f:
            default_criteria = f.read()

        # Загрузка файла паспорта проекта
        passport_file = get_file_uploader(
            "Загрузите паспорт проекта (PDF/DOCX)", ["pdf", "docx"]
        )
        # Загрузка файла отчета по проекту
        report_file = get_file_uploader(
            "Загрузите отчет по проекту (PDF/DOCX)", ["pdf", "docx"]
        )

        with st.expander("Критерии проверки проектов (по умолчанию):", icon="📄"):
            st.markdown(default_criteria)

        # Загрузка новых критериев для проверки,
        # если включен соответствующий переключатель
        new_criteria_file = (
            get_file_uploader(
                "Загрузите критерии для проверки (TXT/PDF/DOCX)",
                ["txt", "pdf", "docx"]
            )
            if st.toggle("Актуализировать критерии проверки проектов")
            else None
        )

        # Выбор модели LLM
        llm_choice = select_llm()
        st.session_state["llm_choice"] = llm_choice

        # Проверка отчета по проекту при нажатии кнопки
        if st.button("🔍 Проверить отчет"):
            if report_file:
                # Проверка наличия файлов
                check_file_uploads(passport_file, new_criteria_file)

                # Сохранение загруженных файлов
                files_to_save = {
                    "passport": passport_file,
                    "report": report_file,
                    "criteria": new_criteria_file if new_criteria_file else None,
                }

                saved_files = {}
                for key, file in files_to_save.items():
                    if file:
                        saved_files[key] = save_file(file)

                # Извлечение текста из сохраненных файлов
                inputs = {
                    "passport": (
                        extract_text_from_file(saved_files.get("passport", ""))
                        if passport_file
                        else ""
                    ),
                    "report": (
                        extract_text_from_file(saved_files.get("report", ""))
                        if report_file
                        else ""
                    ),
                    "criteria": (
                        extract_text_from_file(saved_files.get("criteria", ""))
                        if new_criteria_file
                        else default_criteria
                    ),
                }

                try:
                    # Конфигурация и запуск графа для проверки
                    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
                    graph.invoke(inputs, config=config)

                    # Получение адаптированных критериев проверки
                    check_criteria = graph.get_state(config=config).values[
                        "structured_criteria"
                    ]
                    # Получение результатов проверки
                    check_result = graph.get_state(config=config).values[
                        "check_results"
                    ]

                    # Отображение адаптированных критериев проверки
                    with st.expander("Адаптированные критерии проверки:", icon="📄"):
                        st.markdown(check_criteria)

                    # Отображение результатов проверки
                    with st.expander("Результаты проверки:", icon="📄"):
                        st.markdown(check_result)
                except Exception as e:
                    # Обработка ошибок при проверке
                    st.error(
                        "При проверке возникла ошибка. Пожалуйста попробуйте снова.",
                        icon="😞",
                    )
                    st.exception(e)
                finally:
                    # Удаление сохраненных файлов после обработки
                    delete_files(saved_files.values())
            else:
                # Вывод ошибки, если отчет по проекту не загружен
                st.error("Для запуска проверки необходимо загрузить отчет по проекту.")

    with tab2:
        prompt_manager.render_prompt_editor()


if __name__ == "__main__":
    main()
