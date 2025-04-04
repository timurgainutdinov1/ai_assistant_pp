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
            "YandexGPT",
            "Gemini 2.0 Pro",
            "Gemma 3 27B",
            "Gemini 2.0 Flash",
            "Llama 3.3 70B Instruct",
            "Qwen 32B",
            "Qwen 2.5 72B",
            "Mistral Small 24B",
        ],
    )
