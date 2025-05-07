import argparse
import logging
import os
import shutil

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="Создание директории проекта для AI ассистента"
    )

    parser.add_argument(
        "--project_dir",
        "-p",
        type=str,
        required=True,
        help="Название директории проекта (будет создана в корневой директории)",
    )

    return parser.parse_args()


def create_directory_structure(project_dir):
    """Создание структуры директорий проекта"""
    # Создаем основную директорию проекта
    os.makedirs(project_dir, exist_ok=True)

    # Создаем директории для входных файлов
    input_dir = os.path.join(project_dir, "input")
    reports_dir = os.path.join(input_dir, "reports")
    passports_dir = os.path.join(input_dir, "passports")
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(passports_dir, exist_ok=True)

    return {
        "project_dir": project_dir,
        "input_dir": input_dir,
        "reports_dir": reports_dir,
        "passports_dir": passports_dir,
    }


def create_criteria_file(project_dir):
    """Создание файла с критериями"""

    criteria_path_src = "Критерии.txt"
    criteria_path_dst = os.path.join(project_dir, "Критерии.txt")

    shutil.copy(criteria_path_src, criteria_path_dst)


def create_sample_prompts(project_dir):
    """Создание промптов"""

    prompts_dir_src = "prompts"
    prompts_dir_dst = os.path.join(project_dir, "prompts")

    if os.path.exists(prompts_dir_dst):
        shutil.rmtree(prompts_dir_dst)

    shutil.copytree(prompts_dir_src, prompts_dir_dst)

    return prompts_dir_dst


def main():
    args = parse_arguments()

    # Создаем структуру директорий
    dirs = create_directory_structure(args.project_dir)

    # Создаем файл с критериями
    create_criteria_file(dirs["project_dir"])

    # Создаем примеры промптов
    dirs["prompts_dir"] = create_sample_prompts(dirs["project_dir"])

    logging.info(f"✅ Создание проекта завершено успешно!")
    logging.info(f"📁 Директория проекта: {os.path.abspath(dirs['project_dir'])}")
    logging.info(f"📂 Директории в проекте:")
    logging.info(f"   - prompts: для хранения промптов")
    logging.info(f"   - input: для входных файлов")
    logging.info(f"     - input/reports: для хранения отчетов")
    logging.info(f"     - input/passports: для хранения паспортов")
    logging.info(f"📄 Создан файл с критериями:")
    logging.info(f"   - {os.path.join(dirs['project_dir'], 'Критерии.txt')}")


if __name__ == "__main__":
    main()
