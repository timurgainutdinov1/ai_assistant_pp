from typing import Optional

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from graph_functions import criteria_forming, report_check


class PPCheckState(MessagesState):
    """Состояние графа для осуществления проверки."""

    passport: str  # Паспорт проекта
    report: str  # Отчет по проекту
    criteria: str  # Критерии проверки от пользователя
    structured_criteria: Optional[str] = None  # Структурированные критерии
    check_results: Optional[str] = None  # Результаты проверки


builder = StateGraph(PPCheckState)

# Узлы
builder.add_node("Аналитик", criteria_forming)
builder.add_node("Проверяющий", report_check)

# Ребра
builder.add_edge(START, "Аналитик")
builder.add_edge("Аналитик", "Проверяющий")
builder.add_edge("Проверяющий", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
