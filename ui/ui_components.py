import streamlit as st


def get_file_uploader(label, file_types):
    """
    Создает компонент загрузки файлов Streamlit.

    Args:
        label (str): Текст метки, отображаемый над компонентом
                     загрузки файла.
        file_types (list): Список допустимых расширений файлов для
                           загрузки.

    Returns:
        streamlit.UploadedFile: Объект загруженного файла или None,
                                если файл не был загружен.
    """
    return st.file_uploader(label, type=file_types)


def check_file_uploads(passport, criteria):
    """
    Проверяет загруженные файлы и отображает предупреждения
    при их отсутствии через интерфейс Streamlit.

    Args:
        passport: Объект файла с паспортом проекта или None, если
                  файл не загружен.
        criteria: Объект файла с критериями проверки или None, если
                  файл не загружен.
    """
    warnings = []
    if passport is None:
        warnings.append("паспорт проекта не загружен")
    if criteria is None:
        warnings.append("используются критерии проверки по умолчанию")
    if warnings:
        st.warning(f"Предупреждение: {', '.join(warnings)}.")


def select_llm():
    """
    Создает выпадающий список для выбора LLM модели из доступных
    вариантов.

    Returns:
        str: Название выбранной пользователем LLM модели из списка
             доступных моделей.
    """
    return st.selectbox(
        "Выберите LLM:",
        [
            # "GigaChat (Lite)",
            "DeepSeek Chat",
            "DeepSeek R1",
            "YandexGPT Pro",
            "YandexGPT Lite",
            # "Gemini 2.0 Pro",
            # "Gemini 2.5 Pro",
            # "Gemma 3 27B",
            "Gemini 2.0 Flash",
            # "Llama 3.3 70B Instruct",
            "Qwen 32B",
            "Qwen 2.5 72B",
            # "Mistral Small 24B",
        ],
    )


def create_download_section(check_result, html_content, pdf_bytes, file_name_base):
    """
    Создает секцию для скачивания результатов в разных форматах.

    Args:
        check_result (str): Результаты проверки в формате Markdown
        html_content (str): Результаты проверки в формате HTML
        pdf_bytes (bytes): Результаты проверки в формате PDF
        file_name_base (str): Базовое имя файла для скачивания
    """
    # Формирование имен файлов для скачивания
    download_file_name_md = f"{file_name_base}_check_results.md"
    download_file_name_pdf = f"{file_name_base}_check_results.pdf"
    download_file_name_html = f"{file_name_base}_check_results.html"

    # Выбор формата для сохранения
    save_format = st.selectbox(
        "💾 Выберите формат для сохранения результатов:",
        ["HTML", "PDF", "Markdown"],
        index=0,
    )

    # Конфигурация для каждого формата
    format_config = {
        "HTML": {
            "data": html_content,
            "file_name": download_file_name_html,
            "mime": "text/html",
        },
        "PDF": {
            "data": pdf_bytes,
            "file_name": download_file_name_pdf,
            "mime": "application/pdf",
        },
        "Markdown": {
            "data": check_result,
            "file_name": download_file_name_md,
            "mime": "text/plain",
        },
    }

    # Единая кнопка скачивания с параметрами из конфигурации
    config = format_config[save_format]
    st.download_button(label=f"📥 Скачать результаты ({save_format})", **config)


def create_project_upload_section():
    """
    Создает секции загрузки файлов для паспорта и отчета проекта.

    Returns:
        tuple: Пара объектов streamlit.UploadedFile:
            - passport_file (streamlit.UploadedFile): Загруженный паспорт проекта или None
            - report_file (streamlit.UploadedFile): Загруженный отчет проекта или None
    """
    passport_file = get_file_uploader(
        "📄 Загрузите паспорт проекта (PDF/DOCX)", ["pdf", "docx"]
    )
    report_file = get_file_uploader(
        "📝 Загрузите отчет по проекту (PDF/DOCX)", ["pdf", "docx"]
    )
    return passport_file, report_file


def create_criteria_section(default_criteria):
    """
    Создает секцию для отображения и опционального обновления критериев оценки проекта.

    Args:
        default_criteria (str): Текст критериев по умолчанию в формате markdown

    Returns:
        tuple:
            - custom_criteria (bool): Нужно ли использовать пользовательские критерии
            - new_criteria_file (streamlit.UploadedFile): Загруженный файл с критериями или None
    """
    with st.expander("Критерии проверки проектов (по умолчанию):", icon="📋"):
        st.markdown(default_criteria)

    custom_criteria = st.toggle("🔄 Актуализировать критерии проверки проектов")
    new_criteria_file = (
        get_file_uploader(
            "📋 Загрузите критерии для проверки (TXT/PDF/DOCX)", ["txt", "pdf", "docx"]
        )
        if custom_criteria
        else None
    )

    return custom_criteria, new_criteria_file


def create_options_section():
    """
    Создает секцию для настройки параметров оценки проекта.

    Returns:
        tuple:
            - skip_feedback (bool): Пропускать ли генерацию обратной связи для студента
            - llm_choice (str): Название выбранной LLM модели
    """
    skip_feedback = not st.toggle(
        "💬 Формировать обратную связь для студента", value=True
    )
    llm_choice = select_llm()
    return skip_feedback, llm_choice


def create_results_section(check_criteria, check_result, feedback):
    """
    Создает секцию отображения результатов оценки проекта.

    Args:
        check_criteria (str): Адаптированные критерии оценки в формате markdown
        check_result (str): Результаты оценки в формате markdown
        feedback (str): Обратная связь для студента в формате markdown или None
    """
    st.header("📊 Результаты проверки")
    with st.expander("Адаптированные критерии проверки:", icon="📋"):
        st.markdown(check_criteria)

    with st.expander("Результаты проверки:", icon="📝"):
        st.markdown(check_result)

    if feedback:
        with st.expander("Обратная связь для студента:", icon="💬"):
            st.markdown(feedback)


def create_user_feedback_form():
    """
    Создает форму для сбора обратной связи пользователя о результатах проверки.

    Returns:
        tuple:
            - mark (str): Оценка пользователя ("Хорошо" или "Плохо")
            - comment (str): Опциональный комментарий пользователя
            - sent_feedback (bool): Была ли отправлена обратная связь
    """
    with st.expander("Оставить обратную связь о результатах проверки:", icon="⭐"):
        mark = st.radio("Оценка:", ["Хорошо", "Плохо"], index=0)
        comment = st.text_area("Комментарий (необязательно):")
        sent_feedback = st.button("Отправить обратную связь")
        return mark, comment, sent_feedback
