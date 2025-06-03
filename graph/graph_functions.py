import time

import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tenacity import retry, stop_after_attempt

from llm.llm_config import get_llm
from utils.prompt_manager import prompt_manager


@retry(stop=stop_after_attempt(3))
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
        st.session_state["structuring_criteria_duration"] = 0
        return {"structured_criteria": state["criteria"]}
    with st.spinner("Адаптация критериев под проект..."):
        template = prompt_manager.get_prompt("CRITERIA_FORMING_TEMPLATE")
        prompt = ChatPromptTemplate.from_messages([("system", template)])

        chain = prompt | get_llm() | StrOutputParser()

        structured_criteria = state.get("structured_criteria", "")
        start_time = time.time()
        res = chain.invoke(
            {
                "passport": state["passport"],
                "criteria": state["criteria"],
                "structured_criteria": structured_criteria,
            }
        )
        end_time = time.time()
        st.session_state["structuring_criteria_duration"] = end_time - start_time

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

        start_time = time.time()
        res = chain.invoke(
            {
                "report": state["report"],
                "structured_criteria": state["structured_criteria"],
            }
        )
        end_time = time.time()
        st.session_state["checking_report_duration"] = end_time - start_time
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

        start_time = time.time()
        res = chain.invoke({"check_results": state["check_results"]})
        end_time = time.time()
        st.session_state["feedback_forming_duration"] = end_time - start_time

        return {"feedback": res}
