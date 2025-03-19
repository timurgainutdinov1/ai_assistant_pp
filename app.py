import asyncio
import uuid
from datetime import datetime

import streamlit as st

from graph.compile_graph import graph
from prompts.prompt_manager import prompt_manager
from ui.ui_components import (check_file_uploads, create_criteria_section,
                              create_download_section, create_options_section,
                              create_project_upload_section,
                              create_results_section,
                              create_user_feedback_form)
from utils.file_handler import extract_text_from_file
from utils.file_utils import delete_files, save_uploaded_files
from utils.results_handler import handle_check_results, prepare_results_json
from utils.s3_utils import S3Handler, prepare_s3_files, save_to_s3


def main():
    st.title("🤖 AI-ассистент куратора проектного практикума")

    tab1, tab2 = st.tabs(["📋 Проверка проектов", "⚙️ Управление промптами"])

    # Основная вкладка для проверки проектов
    with tab1:
        # Загружаем критерии по умолчанию
        with open("Критерии.txt", "r", encoding="utf-8") as f:
            default_criteria = f.read()

        # Формируем основные элементы интерфейса
        passport_file, report_file = create_project_upload_section()
        custom_criteria, new_criteria_file = create_criteria_section(default_criteria)
        skip_feedback, llm_choice = create_options_section()

        st.session_state["llm_choice"] = llm_choice

        # Запрашиваем согласие на обработку файлов
        consent = st.checkbox("Я согласен на обработку и хранение загруженных файлов для улучшения качества сервиса.", key="consent_checkbox")
        
        start_check = st.button("🔍 Проверить отчет", disabled=not consent)

        if start_check:
            # Очищаем все предыдущие результаты
            keys_to_keep = ["llm_choice"]
            for key in list(st.session_state.keys()):
                if key not in keys_to_keep:
                    del st.session_state[key]

            if report_file:
                # Проверяем загруженные файлы и выводим предупреждение,
                # если файлы не загружены
                check_file_uploads(passport_file, new_criteria_file)

                # Сохраняем загруженные файлы
                files_to_save = {
                    "passport": passport_file,
                    "report": report_file,
                    "criteria": new_criteria_file if new_criteria_file else None,
                }
                st.session_state.files_to_save = files_to_save
                saved_files = save_uploaded_files(files_to_save)

                # Формируем входные данные для графа
                inputs = {
                    "passport": (
                        extract_text_from_file(saved_files.get("passport", ""))
                        if passport_file
                        else ""
                    ),
                    "report": (
                        extract_text_from_file(saved_files.get("report", ""))
                    ),
                    "criteria": (
                        extract_text_from_file(saved_files.get("criteria", ""))
                        if new_criteria_file
                        else default_criteria
                    ),
                    "skip_feedback": skip_feedback,
                }

                try:
                    # Запускаем граф
                    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
                    graph.invoke(inputs, config=config)
                    # Обрабатываем результаты проверки
                    handle_check_results(config, graph, custom_criteria, skip_feedback)
                    st.session_state.report_file_name = report_file.name.split(".")[0]
                    st.session_state.current_time = datetime.now().strftime(
                        "%Y%m%d_%H%M%S"
                    )

                except Exception as e:
                    st.error(
                        "При проверке возникла ошибка. Пожалуйста попробуйте снова.",
                        icon="😞",
                    )
                    st.exception(e)
                finally:
                    # Удаляем загруженные файлы
                    delete_files(list(saved_files.values()))
            else:
                st.error(
                    "⚠️ Для запуска проверки необходимо загрузить отчет по проекту."
                )

    # Вкладка для управления промптами
    with tab2:
        prompt_manager.render_prompt_editor()

    # Секция после проверки
    if "check_result" in st.session_state:
        # Подготавливаем файлы для сохранения в S3
        files_to_s3_save = prepare_s3_files(
            st.session_state.files_to_save,
            st.session_state.check_result,
            st.session_state.check_criteria,
            st.session_state.feedback,
        )

        # Создаем уникальное имя папки для сохранения результатов в S3
        if "folder_name" not in st.session_state:
            st.session_state.folder_name = (
                f"{st.session_state.current_time}_{uuid.uuid4()}"
            )

        # Подготавливаем JSON для сохранения в S3
        results_json = prepare_results_json(
            st.session_state.files_to_save,
            st.session_state.current_time,
            st.session_state.llm_choice,
            st.session_state.passport_content,
            st.session_state.report_content,
            st.session_state.input_criteria,
            st.session_state.check_result,
            st.session_state.check_criteria,
            st.session_state.feedback,
        )
        # Сохраняем результаты в S3
        if not st.session_state.get("s3_save_completed", False):
            if "s3_handler" not in st.session_state:
                st.session_state.s3_handler = S3Handler()

                # Создаем уникальную папку для данной проверки
                st.session_state.s3_handler.set_base_path(st.session_state.folder_name)

            with st.spinner("Сохранение результатов..."):
                asyncio.run(
                    save_to_s3(
                        st.session_state.s3_handler,
                        files_to_s3_save,
                        st.session_state.report_file_name,
                        results_json,
                    )
                )

            # Отмечаем, что сохранение в S3 завершено
            st.session_state.s3_save_completed = True

        # Отображаем результаты проверки, форму обратной связи
        # и кнопку для скачивания результатов
        with tab1:
            # Отображаем результаты проверки
            create_results_section(
                st.session_state.check_criteria,
                st.session_state.check_result,
                st.session_state.feedback,
            )

            # Отображаем форму обратной связи
            # и кнопку для отправки обратной связи
            mark, comment, sent_feedback = create_user_feedback_form()

            # Если пользователь отправил обратную связь,
            # перезаписываем результаты в JSON в S3
            if sent_feedback:
                results_json["feedback_from_user"]["rating"] = mark
                results_json["feedback_from_user"]["comment"] = comment
                with st.spinner("Сохранение обратной связи..."):
                    asyncio.run(
                        st.session_state.s3_handler.save_results_json_to_s3(
                            results_json
                        )
                    )
                st.success("Благодарим за обратную связь!")

            # Формируем имя файла для скачивания результатов
            file_name_base = (
                f"{st.session_state.llm_choice}_"
                f"{st.session_state.current_time}_"
                f"{st.session_state.report_file_name}"
            )

            # Отображаем кнопку для скачивания результатов
            create_download_section(
                st.session_state.check_result,
                st.session_state.html_content,
                st.session_state.pdf_bytes,
                file_name_base,
            )


if __name__ == "__main__":
    main()
