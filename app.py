import uuid
from datetime import datetime

import streamlit as st

from compile_graph import graph
from file_handler import extract_text_from_file
from file_utils import (convert_markdown_to_html, convert_markdown_to_pdf,
                        delete_files, save_file)
from prompt_manager import prompt_manager
from ui_components import check_file_uploads, get_file_uploader, select_llm


def main():
    st.title("🤖 AI-ассистент куратора проектного практикума")

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
                "Загрузите критерии для проверки (TXT/PDF/DOCX)", ["txt", "pdf", "docx"]
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

                    # Сохраняем результаты в session state
                    st.session_state.check_result = check_result
                    st.session_state.check_criteria = check_criteria
                    st.session_state.pdf_bytes = convert_markdown_to_pdf(check_result)
                    st.session_state.html_content = convert_markdown_to_html(
                        check_result
                    )
                    st.session_state.report_file_name = report_file.name.split(".")[0]
                    st.session_state.llm_choice = llm_choice
                    st.session_state.current_time = datetime.now().strftime(
                        "%Y%m%d_%H%M%S"
                    )

                except Exception as e:
                    # Обработка ошибок при проверке
                    st.error(
                        "При проверке возникла ошибка. Пожалуйста попробуйте снова.",
                        icon="😞",
                    )
                    st.exception(e)
                finally:
                    # Удаление сохраненных файлов после обработки
                    delete_files(list(saved_files.values()))
            else:
                # Вывод ошибки, если отчет по проекту не загружен
                st.error("Для запуска проверки необходимо загрузить отчет по проекту.")

    with tab2:
        prompt_manager.render_prompt_editor()

    # Формат сохранения и кнопка скачивания
    if "check_result" in st.session_state:

        st.header("Результаты проверки")
        # Отображение адаптированных критериев проверки
        with st.expander("Адаптированные критерии проверки:", icon="📄"):
            st.markdown(st.session_state.check_criteria)

        # Отображение результатов проверки
        with st.expander("Результаты проверки:", icon="📄"):
            st.markdown(st.session_state.check_result)

        # Формирование имен файлов для скачивания
        file_name_base = (f"{st.session_state.llm_choice}_"
                         f"{st.session_state.current_time}_"
                         f"{st.session_state.report_file_name}")
        
        download_file_name_md = f"{file_name_base}_check_results.md"
        download_file_name_pdf = f"{file_name_base}_check_results.pdf"
        download_file_name_html = f"{file_name_base}_check_results.html"

        # Выбор формата для сохранения
        save_format = st.selectbox(
            "Выберите формат для сохранения результатов:",
            ["HTML", "PDF", "Markdown"],
            index=0,
        )

        # Отображение кнопки скачивания в выбранном формате
        if save_format == "HTML":
            st.download_button(
                label="Скачать результаты (HTML)",
                data=st.session_state.html_content,
                file_name=download_file_name_html,
                mime="text/html",
            )
        elif save_format == "PDF":
            st.download_button(
                label="Скачать результаты (PDF)",
                data=st.session_state.pdf_bytes,
                file_name=download_file_name_pdf,
                mime="application/pdf",
            )
        else:  # Markdown
            st.download_button(
                label="Скачать результаты (Markdown)",
                data=st.session_state.check_result,
                file_name=download_file_name_md,
                mime="text/plain",
            )


if __name__ == "__main__":
    main()
