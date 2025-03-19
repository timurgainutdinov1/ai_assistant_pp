from streamlit import session_state
from typing import Dict, Any, Optional
from utils.file_utils import convert_markdown_to_pdf, convert_markdown_to_html


def handle_check_results(config: Dict[str, Any], graph: Any, custom_criteria: bool, skip_feedback: bool) -> None:
    """
    Обрабатывает результаты проверки проекта и сохраняет их в session_state.

    Args:
        config (Dict[str, Any]): Конфигурация для графа
        graph (Any): Объект графа для получения результатов
        custom_criteria (bool): Флаг использования пользовательских критериев
        skip_feedback (bool): Флаг пропуска генерации обратной связи
    """
    session_state.passport_content = graph.get_state(config=config).values["passport"]
    session_state.report_content = graph.get_state(config=config).values["report"]
    session_state.check_result = graph.get_state(config=config).values["check_results"]
    session_state.input_criteria = (
        graph.get_state(config=config).values["criteria"]
        if custom_criteria
        else ""
    )
    session_state.check_criteria = graph.get_state(config=config).values["structured_criteria"]
    session_state.feedback = (
        None
        if skip_feedback
        else graph.get_state(config=config).values["feedback"]
    )
    session_state.pdf_bytes = convert_markdown_to_pdf(session_state.check_result)
    session_state.html_content = convert_markdown_to_html(session_state.check_result)

def prepare_results_json(
    files_to_save: Dict[str, Any],
    current_time: str,
    llm_choice: str,
    passport_content: str,
    report_content: str,
    input_criteria: str,
    check_result: str,
    check_criteria: Dict[str, Any],
    feedback: Optional[str]
) -> Dict[str, Any]:
    """
    Подготавливает JSON с результатами проверки проекта.

    Args:
        files_to_save (Dict[str, Any]): Словарь с загруженными файлами
        current_time (str): Текущее время
        llm_choice (str): Выбранная LLM модель
        passport_content (str): Содержимое паспорта проекта
        report_content (str): Содержимое отчета
        input_criteria (str): Входные критерии оценки
        check_result (str): Результаты проверки
        check_criteria (Dict[str, Any]): Структурированные критерии оценки
        feedback (Optional[str]): Обратная связь для студента

    Returns:
        Dict[str, Any]: JSON с результатами проверки, включая входные данные,
                        выходные результаты и метаданные
    """
    return {
        "timestamp": current_time,
        "llm": llm_choice,
        "inputs": {
            "names": [file.name for file in files_to_save.values() if file is not None],
            "content": {
                "passport": passport_content,
                "report": report_content,
                "criteria": input_criteria,
            }
        },
        "outputs": {
            "content": {
                "check_results": check_result,
                "check_criteria": check_criteria,
                "feedback_for_student": feedback,
            }
        },
        "feedback_from_user": {},
    }
