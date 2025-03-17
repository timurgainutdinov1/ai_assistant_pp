from typing import Optional

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from graph_functions import criteria_forming, report_check, feedback_forming


class PPCheckState(MessagesState):
    """Состояние графа для осуществления проверки."""

    passport: str  # Паспорт проекта
    report: str  # Отчет по проекту
    criteria: str  # Критерии проверки от пользователя
    structured_criteria: Optional[str] = None  # Структурированные критерии
    check_results: Optional[str] = None  # Результаты проверки
    feedback: Optional[str] = None  # Обратная связь для студента
    skip_feedback: bool = False  # Флаг для пропуска этапа формирования обратной связи


builder = StateGraph(PPCheckState)

# Узлы
builder.add_node("Аналитик", criteria_forming)
builder.add_node("Проверяющий", report_check)
builder.add_node("Преподаватель", feedback_forming)

# Ребра
builder.add_edge(START, "Аналитик")
builder.add_edge("Аналитик", "Проверяющий")


# Условное ребро для этапа обратной связи
def should_form_feedback(state):
    return not state["skip_feedback"]


builder.add_conditional_edges(
    "Проверяющий", should_form_feedback, {True: "Преподаватель", False: END}
)
builder.add_edge("Преподаватель", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
