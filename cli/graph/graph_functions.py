import os

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tenacity import retry, stop_after_attempt, wait_exponential

from cli.llm.llm_config import get_llm


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=15))
def criteria_forming(state):
    """
    Адаптирует критерии оценки под конкретный проект.

    Args:
        state (dict): Словарь состояния, содержащий:
            - passport (str): Паспорт проекта
            - criteria (str): Исходные критерии оценки
            - structured_criteria (str): Структурированные критерии оценки

    Returns:
        dict: Словарь с ключом 'structured_criteria', содержащий
              адаптированные критерии
    """
    if not state["passport"]:
        return {"structured_criteria": state["criteria"]}

    project_dir = os.environ["PROJECT_DIR"]
    with open(
        os.path.join(project_dir, "prompts", "criteria_forming.txt"),
        "r",
        encoding="utf-8",
    ) as file:
        template = file.read()

    prompt = ChatPromptTemplate.from_messages([("system", template)])

    chain = prompt | get_llm() | StrOutputParser()

    structured_criteria = state.get("structured_criteria", "")
    res = chain.invoke(
        {
            "passport": state["passport"],
            "criteria": state["criteria"],
            "structured_criteria": structured_criteria,
        }
    )

    return {"structured_criteria": res}


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=15))
def report_check(state):
    """
    Проверяет отчет на соответствие структурированным критериям.

    Args:
        state (dict): Словарь состояния, содержащий:
            - report (str): Текст отчета для проверки
            - structured_criteria (str): Структурированные критерии оценки

    Returns:
        dict: Словарь с ключом 'check_results', содержащий результаты проверки
    """
    project_dir = os.environ["PROJECT_DIR"]
    with open(
        os.path.join(project_dir, "prompts", "check_report.txt"), "r", encoding="utf-8"
    ) as file:
        template = file.read()

    prompt = ChatPromptTemplate.from_messages([("system", template)])

    chain = prompt | get_llm() | StrOutputParser()

    res = chain.invoke(
        {
            "report": state["report"],
            "structured_criteria": state["structured_criteria"],
        }
    )

    return {"check_results": res}


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=15))
def feedback_forming(state):
    """
    Формирует дружелюбную обратную связь для студента на основе результатов проверки.

    Args:
        state (dict): Словарь состояния, содержащий:
            - check_results (str): Результаты проверки отчета

    Returns:
        dict: Словарь с ключом 'feedback', содержащий сформированную обратную связь
    """
    project_dir = os.environ["PROJECT_DIR"]
    with open(
        os.path.join(project_dir, "prompts", "feedback_forming.txt"),
        "r",
        encoding="utf-8",
    ) as file:
        template = file.read()

    prompt = ChatPromptTemplate.from_messages([("system", template)])

    chain = prompt | get_llm() | StrOutputParser()

    res = chain.invoke({"check_results": state["check_results"]})

    return {"feedback": res}
