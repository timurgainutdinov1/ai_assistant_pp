import os
import uuid
from io import BytesIO

import markdown2
from fpdf import FPDF

import logging

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader


def save_file(file, name=None):
    """
    Сохраняет загруженный файл с уникальным идентификатором.

    Args:
        file: Объект загруженного файла.
        name (str, optional): Пользовательское имя для файла.
                              Если не указано, используется оригинальное имя.

    Returns:
        str: Имя сохраненного файла с уникальным идентификатором.
    """
    unique_id = str(uuid.uuid4())
    file_name = f"{unique_id}_{name if name else file.name}"
    with open(file_name, "wb") as f:
        f.write(file.getbuffer())
    return file_name


def delete_files(files):
    """
    Удаляет указанные файлы из файловой системы.

    Args:
        files (list): Список путей к файлам, которые необходимо удалить.
    """
    for file in files:
        if file:
            os.remove(file)


def convert_markdown_to_pdf(markdown_content):
    """
    Конвертирует текст в формате Markdown в PDF документ.

    Args:
        markdown_content (str): Текст в формате Markdown для конвертации.

    Returns:
        BytesIO: PDF документ в виде объекта BytesIO.
    """
    html_text = markdown2.markdown(markdown_content)

    pdf = FPDF()
    pdf.add_page()
    font_path = "fonts/"

    pdf.add_font("NotoSans", "", f"{font_path}NotoSans-Regular.ttf", uni=True)
    pdf.add_font("NotoSans", "B", f"{font_path}NotoSans-Bold.ttf", uni=True)
    pdf.add_font("NotoSans", "I", f"{font_path}NotoSans-Italic.ttf", uni=True)
    pdf.add_font("NotoSans", "BI", f"{font_path}NotoSans-BoldItalic.ttf", uni=True)

    pdf.set_font("NotoSans", size=12)
    pdf.write_html(html_text)

    pdf_output = BytesIO()
    pdf.output(pdf_output, "F")
    pdf_output.seek(0)
    return pdf_output


def convert_markdown_to_html(markdown_content):
    """
    Конвертирует текст в формате Markdown в HTML документ.

    Args:
        markdown_content (str): Текст в формате Markdown для конвертации.

    Returns:
        str: HTML документ с встроенными стилями и поддержкой MathJax.

    Особенности:
        - Поддерживает блоки кода
        - Поддерживает таблицы
        - Включает MathJax для математических формул
        - Содержит встроенные CSS стили
    """
    html_text = markdown2.markdown(
        markdown_content, extras=["fenced-code-blocks", "tables"]
    )

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 40px auto; 
                padding: 0 20px; 
            }}
            pre {{ 
                background-color: #f5f5f5; 
                padding: 15px; 
                border-radius: 5px; 
            }}
            table {{ 
                border-collapse: collapse; 
                width: 100%; 
            }}
            th, td {{ 
                border: 1px solid #ddd; 
                padding: 8px; 
            }}
            th {{ 
                background-color: #f5f5f5; 
            }}
        </style>
    </head>
    <body>
        {}
    </body>
    </html>
    """.format(
        html_text
    )
    return html_template


def save_uploaded_files(files_to_save):
    """
    Сохраняет загруженные файлы во временную директорию.

    Args:
        files_to_save (dict): Словарь с загруженными файлами, где ключ -
                             идентификатор файла, значение - объект файла.

    Returns:
        dict: Словарь с путями к сохраненным файлам, где ключ - идентификатор
              файла, значение - путь к сохраненному файлу.
    """
    saved_files = {}
    for key, file in files_to_save.items():
        if file:
            saved_files[key] = save_file(file)
    return saved_files


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
