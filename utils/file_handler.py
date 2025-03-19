import logging

from langchain_community.document_loaders import (Docx2txtLoader, PyPDFLoader,
                                                  TextLoader)


def extract_text_from_file(uploaded_file: str) -> str:
    """
    Извлекает текстовое содержимое из файлов PDF, DOCX или TXT.

    Args:
        uploaded_file (str): Путь к загруженному файлу.

    Returns:
        str: Извлеченный текст из файла. Возвращает пустую строку,
             если формат файла не поддерживается
             или произошла ошибка при чтении.

    Поддерживаемые форматы файлов:
        - .pdf: Использует PyPDFLoader для извлечения текста со всех страниц.
        - .docx: Использует Docx2txtLoader для извлечения текстового
                 содержимого.
        - .txt: Использует TextLoader с автоопределением кодировки.
    """
    try:
        if uploaded_file.endswith(".docx"):
            text = Docx2txtLoader(uploaded_file).load()[0].page_content
        elif uploaded_file.endswith(".pdf"):
            pages = PyPDFLoader(uploaded_file).load()
            text = "\n".join(page.page_content for page in pages)
        elif uploaded_file.endswith(".txt"):
            text = (
                TextLoader(uploaded_file, autodetect_encoding=True)
                .load()[0]
                .page_content
            )
        else:
            text = ""
            logging.warning(f"Неподдерживаемый формат файла: {uploaded_file}")
        return text
    except Exception as e:
        logging.error(f"Ошибка при чтении файла {uploaded_file}: {str(e)}")
        return ""
