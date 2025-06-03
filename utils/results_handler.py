from typing import Any, Dict, Optional

from streamlit import session_state

from utils.file_utils import convert_markdown_to_html, convert_markdown_to_pdf


def handle_check_results(
    config: Dict[str, Any], graph: Any, custom_criteria: bool, skip_feedback: bool
) -> None:
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
        graph.get_state(config=config).values["criteria"] if custom_criteria else ""
    )
    session_state.check_criteria = graph.get_state(config=config).values[
        "structured_criteria"
    ]
    session_state.feedback = (
        None if skip_feedback else graph.get_state(config=config).values["feedback"]
    )
    session_state.pdf_bytes = convert_markdown_to_pdf(session_state.check_result)
    session_state.html_content = convert_markdown_to_html(session_state.check_result)


def prepare_results_json() -> Dict[str, Any]:
    """
    Подготавливает JSON с результатами проверки проекта.
    Все данные извлекаются из session_state.

    Returns:
        Dict[str, Any]: JSON с результатами проверки, включая входные данные,
                        выходные результаты и метаданные
    """
    return {
        "timestamp": session_state.current_time,
        "session_id": session_state.session_id,
        "llm": session_state.llm_choice,
        "duration": session_state.duration,
        "structuring_criteria_duration": session_state.structuring_criteria_duration,
        "checking_report_duration": session_state.checking_report_duration,
        "feedback_forming_duration": session_state.feedback_forming_duration,
        "inputs": {
            "names": [
                file.name
                for file in session_state.files_to_save.values()
                if file is not None
            ],
            "content": {
                "passport": session_state.passport_content,
                "report": session_state.report_content,
                "criteria": session_state.input_criteria,
            },
        },
        "outputs": {
            "content": {
                "check_results": session_state.check_result,
                "check_criteria": session_state.check_criteria,
                "feedback_for_student": session_state.feedback,
            }
        },
        "feedback_from_user": {},
    }
