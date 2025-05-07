import argparse
import json
import logging
import os
from datetime import datetime

from tqdm import tqdm

from cli.graph.compile_graph import graph
from utils.file_utils import extract_text_from_file


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="AI-ассистент куратора проектного практикума (консольная версия)"
    )

    parser.add_argument(
        "--project_dir",
        "-p",
        type=str,
        default="project",
        help="Путь к директории с проектом",
    )
    parser.add_argument(
        "--reports_dir",
        "-reports",
        type=str,
        default="input/reports",
        help="Путь к директории c отчетами",
    )
    parser.add_argument(
        "--passports_dir",
        "-passports",
        type=str,
        default="input/passports",
        help="Путь к директории c паспортами",
    )
    parser.add_argument(
        "--criteria_file_path",
        "-c",
        type=str,
        default="Критерии.txt",
        help="Путь к файлу с критериями оценки (TXT)",
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        type=str,
        default="output",
        help="Директория для сохранения результатов",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="DeepSeek Chat",
        help="Название LLM модели для использования",
    )
    parser.add_argument(
        "--skip-feedback",
        "-s",
        action="store_true",
        help="Пропустить этап генерации обратной связи для студента",
    )

    return parser.parse_args()


def setup_environment(args, output_dir):
    """Настройка окружения"""
    # Создаем директорию для результатов, если она не существует
    os.makedirs(output_dir, exist_ok=True)

    # Устанавливаем модель LLM и путь к директории с проектом
    os.environ["LLM_MODEL"] = args.model
    os.environ["PROJECT_DIR"] = args.project_dir


def load_criteria(criteria_file_path):
    """Загрузка критериев"""
    if not os.path.isfile(criteria_file_path):
        logging.error(f"Файл с критериями не найден: {criteria_file_path}")
        raise FileNotFoundError(f"Файл с критериями не найден: {criteria_file_path}")

    criteria = extract_text_from_file(criteria_file_path)
    return criteria


def read_file_content(file_path):
    """Чтение содержимого файла"""
    if not file_path:
        raise ValueError("Не указан путь к файлу")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    return extract_text_from_file(file_path)


def save_results(file_name, results, output_dir, skip_feedback):
    """Сохранение результатов проверки"""

    base_result_path = os.path.join(output_dir, os.path.splitext(file_name)[0])
    result_path = base_result_path
    
    # Проверка на существование файлов и добавление уникального суффикса при необходимости
    counter = 1
    while os.path.exists(f"{result_path}_check_results.md"):
        result_path = f"{base_result_path}_{counter}"
        counter += 1

    # Сохраняем результаты проверки
    with open(f"{result_path}_check_results.md", "w", encoding="utf-8") as f:
        f.write(results.get("check_results", ""))

    # Сохраняем структурированные критерии проверки
    with open(f"{result_path}_criteria.md", "w", encoding="utf-8") as f:
        f.write(results.get("criteria", ""))

    # Сохраняем обратную связь для студента
    if not skip_feedback:
        with open(f"{result_path}_feedback.md", "w", encoding="utf-8") as f:
            f.write(results.get("feedback", ""))


def check_input_format(reports_dir, passports_dir):
    """Проверка формата входных файлов"""

    supported_formats = (".txt", ".pdf", ".docx")

    dirs = [reports_dir, passports_dir]
    for dir in dirs:
        for file_name in os.listdir(dir):
            if not file_name.endswith(supported_formats):
                logging.error(f"Неверный формат входного файла: {file_name}, допустимые форматы: {supported_formats}.")
                raise ValueError(f"Неверный формат входного файла: {file_name}, допустимые форматы: {supported_formats}.")


def main():

    args = parse_arguments()

    project_dir = args.project_dir
    reports_dir = os.path.join(project_dir, args.reports_dir)
    passports_dir = os.path.join(project_dir, args.passports_dir)
    output_dir = os.path.join(project_dir, args.output_dir)
    criteria_file_path = os.path.join(project_dir, args.criteria_file_path)
    status_file_path = os.path.join(project_dir, "docs_status.json")
    skip_feedback = args.skip_feedback

    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler(
                os.path.join(project_dir, "ai_assistant_pp.log"),
                mode="a",
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Проверяем формат входных файлов
    check_input_format(reports_dir, passports_dir)

    # Настраиваем окружение
    setup_environment(args, output_dir)

    # Загружаем критерии
    criteria = load_criteria(criteria_file_path)

    # Загружаем статусы обработки файлов
    try:
        with open(status_file_path, "r", encoding="utf-8") as f:
            docs_status = json.load(f)
    except FileNotFoundError:
        docs_status = {}

    # Проверяем наличие паспортов
    has_passports = len(os.listdir(passports_dir)) > 0
    if not has_passports:
        logging.warning(
            "Папка с паспортами пуста. Адаптация критериев с учетом паспорта выполнена не будет."
        )

    processed_passports = []
    # Обрабатываем отчеты
    for file_name in tqdm(os.listdir(reports_dir), desc="Обработка отчетов"):

        # Пропускаем обработку файлов, если они уже были обработаны
        if file_name in docs_status:
            if docs_status[file_name]["status"] == "success":
                continue

        # Инициализируем статусы обработки файлов
        docs_status[file_name] = dict.fromkeys(
            ["status", "error_message", "processed_at"]
        )

        try:
            report = read_file_content(os.path.join(reports_dir, file_name))
            report_file_name = os.path.splitext(file_name)[0]

            passport = ""

            # Ищем паспорт, если он есть
            if has_passports:
                for passport_file in os.listdir(passports_dir):
                    if (
                        report_file_name.lower() in passport_file.lower()
                        and passport_file not in processed_passports
                    ):
                        passport = read_file_content(
                            os.path.join(passports_dir, passport_file)
                        )
                        processed_passports.append(passport_file)
                        break

            results = graph.invoke(
                {
                    "report": report,
                    "criteria": criteria,
                    "passport": passport,
                    "skip_feedback": skip_feedback,
                }
            )

            # Сохраняем результаты проверки
            save_results(file_name, results, output_dir, skip_feedback)
            docs_status[file_name]["status"] = "success"
            logging.info(f"✅ Файл {file_name} успешно обработан")
        except Exception as e:
            docs_status[file_name]["status"] = "error"
            docs_status[file_name]["error_message"] = str(e)
            logging.error(f"Ошибка при обработке файла {file_name}: {str(e)}")
        finally:
            # Сохраняем время, в которое был обработан файл
            docs_status[file_name]["processed_at"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    logging.info("✅ Проверка завершена успешно!")
    logging.info(f"📁 Результаты сохранены в: {output_dir}")

    with open(status_file_path, "w", encoding="utf-8") as f:
        json.dump(docs_status, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
