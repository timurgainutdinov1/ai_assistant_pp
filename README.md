# 🤖 AI-ассистент куратора проектного практикума

![](assets/logo.png)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aiassistpp.streamlit.app/)


## 📋 О проекте

AI-ассистент куратора проектного практикума — это сервис для автоматизации проверки отчетов по студенческим проектам. Основная цель проекта — снизить нагрузку на преподавателей и ускорить предоставление обратной связи студентам.

## ✨ Функциональность

Сервис выполняет автоматическую проверку студенческих отчетов на основе заданных критериев с использованием языковых моделей (LLM), LangChain и LangGraph.

## 🔄 Как работает сервис

1. **📤 Загрузка материалов** — Пользователь загружает отчет по проекту и опционально паспорт проекта (поддерживаются различные форматы файлов).

2. **⚙️ Настройка критериев** — Пользователь может использовать стандартные критерии оценки или загрузить собственные.

3. **🔍 Анализ и проверка** — Система анализирует загруженные документы с помощью LLM и проверяет соответствие отчета заданным критериям.

4. **📊 Результаты проверки** — Пользователь получает структурированные результаты проверки.

5. **💬 Обратная связь** — Система формирует конструктивную и дружелюбную обратную связь для студента, которую преподаватель может использовать непосредственно или адаптировать.

6. **📥 Выгрузка результатов** — Возможность скачать результаты проверки в удобном формате для дальнейшего использования.

## 🛠️ Технологии

- **🌊 Streamlit** — для создания веб-интерфейса
- **⛓️ LangChain** — для работы с языковыми моделями
- **📊 LangGraph** — для построения графов обработки данных

## 🌐 Доступ к сервису

Вы можете использовать сервис по адресу: [https://aiassistpp.streamlit.app/](https://aiassistpp.streamlit.app/)


## 💻 Локальный запуск Streamlit-приложения

Для запуска проекта локально необходимо:

1. Клонировать репозиторий
2. Создать и активировать виртуальное окружение:
   - `python -m venv [имя виртуального окружения]`
   - для Linux: `source [имя виртуального окружения]/bin/activate`
   - для Windows: `[имя виртуального окружения]\Scripts\activate`
3. Установить зависимости: `pip install -r requirements.txt`
4. Настроить переменные окружения в файле `secrets.toml` (см. `.streamlit/secrets.toml.example`).  
   Если не планируется использование LLM определенного провайдера, то можно оставить поле пустым.
5. Запустить приложение: `streamlit run app.py`

## 📦 Локальный запуск CLI-приложения

Для запуска проекта локально необходимо:

1. Клонировать репозиторий
2. Создать и активировать виртуальное окружение:
   - `python -m venv [имя виртуального окружения]`
   - для Linux: `source [имя виртуального окружения]/bin/activate`
   - для Windows: `[имя виртуального окружения]\Scripts\activate`
3. Установить зависимости: `pip install -r requirements.txt`
4. Настроить переменные окружения в файле `.env` (см. `.env.example`).  
   Если не планируется использование LLM определенного провайдера, то соответствующие поля можно оставить пустыми.
5. Инициализировать проект: `python init_project.py --project_dir [путь к директории с проектом]`

   В результате выполнения скрипта в папке с проектом будут созданы следующие директории и файлы:
   - `input/reports` — директория для загрузки отчетов
   - `input/passports` — директория для загрузки паспортов
   - `Критерии.txt` — файл с критериями проверки
   - `prompts` — директория для хранения промптов

6. При желании можно настроить промпты для проверки в директории `prompts`:
   - `criteria_forming.txt` — промпт для формирования структурированных критериев на основе паспорта проекта
   - `check_report.txt` — промпт для проверки отчета, анализирует отчет по критериям и выставляет оценку
   - `feedback_forming.txt` — промпт для формирования конструктивной обратной связи студенту на основе результатов проверки

   ⚠️ **Важно!** При редактировании промптов необходимо сохранять все поля-заполнители (placeholders) в исходном виде, так как они используются для подстановки данных в процессе работы приложения.

7. При желании можно настроить критерии проверки в файле `Критерии.txt`.

8. Необходимо поместить файлы с отчетами и паспортами в директории `input/reports` и `input/passports` соответственно. Допустимые форматы файлов: `.pdf`, `.docx`.  
   Паспорт для проекта является необязательным. Если он не загружен, то адаптация критериев под требования паспорта проводиться не будет.

   ⚠️ **Важно!** Паспорта проектов должны иметь в своем названии наименование файла с отчетом по проекту, например:
   - Отчет команды 1.pdf — отчет по проекту
   - Отчет команды 1 (паспорт).pdf — паспорт по проекту

9. Запустить приложение: `python cli_app.py --project_dir [путь к директории с проектом]`.  
   По умолчанию используется модель `Deepseek Chat`. Если необходимо использовать другую модель, то можно указать ее при помощи параметра `--model [наименование модели]`.  
   Также можно пропустить этап формирования обратной связи для студента при помощи параметра `--skip-feedback`.  
   Пример запуска без обратной связи и с использованием модели `Gemini 2.0 Flash`: `python cli_app.py --project_dir my_project --model "Gemini 2.0 Flash" --skip-feedback`.

10. Результаты проверки будут сохранены в директории `output` в формате `.md`.  
    Для каждого проверенного отчета будут созданы следующие файлы:
    - `[наименование отчета]_check_results.md` — результаты проверки
    - `[наименование отчета]_criteria.md` — критерии проверки (адаптированные под паспорт проекта или исходные)
    - `[наименование отчета]_feedback.md` — обратная связь для студента (если параметр `--skip-feedback` при запуске не указан)
    
    Также в директории с проектом будет создан файл `docs_status.json` с информацией о статусе проверки каждого документа.
    Если проверка какого-либо отчета завершилась с ошибкой, то в файл будет записан соответствующий статус.
    
    При необходимости можно запустить проверку снова, при этом будут пропущены все отчеты, которые были успешно проверены ранее.
    
    Для удобства в процессе проверки формируется файл с логами `ai_assistant_pp.log`, который сохраняется в директорию с проектом.
