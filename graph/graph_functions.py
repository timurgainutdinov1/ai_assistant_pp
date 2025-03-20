import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from llm.llm_config import get_llm
from utils.prompt_manager import prompt_manager
from tenacity import retry, stop_after_attempt


@retry(stop=stop_after_attempt(3))
def criteria_forming(state):
    """
    Адаптирует критерии оценки под конкретный проект.

    Args:
        state (dict): Словарь состояния, содержащий:
            - passport (str): Паспорт проекта
            - criteria (str): Исходные критерии оценки
            - structured_criteria (str, optional): Ранее структурированные
                                                   критерии

    Returns:
        dict: Словарь с ключом 'structured_criteria', содержащий
              адаптированные критерии
    """
    if not state["passport"]:
        return {"structured_criteria": state["criteria"]}
    with st.spinner("Адаптация критериев под проект..."):
        template = prompt_manager.get_prompt("CRITERIA_FORMING_TEMPLATE")
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


@retry(stop=stop_after_attempt(3))
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
    with st.spinner("Проверка отчета..."):
        template = prompt_manager.get_prompt("CHECK_REPORT_TEMPLATE")
        prompt = ChatPromptTemplate.from_messages([("system", template)])

        chain = prompt | get_llm() | StrOutputParser()

        res = chain.invoke(
            {
                "report": state["report"],
                "structured_criteria": state["structured_criteria"],
            }
        )

        return {"check_results": res}


@retry(stop=stop_after_attempt(3))
def feedback_forming(state):
    """
    Формирует дружелюбную обратную связь для студента на основе результатов проверки.

    Args:
        state (dict): Словарь состояния, содержащий:
            - check_results (str): Результаты проверки отчета

    Returns:
        dict: Словарь с ключом 'feedback', содержащий сформированную обратную связь
    """
    with st.spinner("Формирование обратной связи для студента..."):
        template = prompt_manager.get_prompt("FEEDBACK_FORMING_TEMPLATE")
        prompt = ChatPromptTemplate.from_messages([("system", template)])

        chain = prompt | get_llm() | StrOutputParser()

        res = chain.invoke({"check_results": state["check_results"]})

        return {"feedback": res}
