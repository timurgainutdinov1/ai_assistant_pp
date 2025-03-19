import os
from typing import Dict, Optional

import streamlit as st


class PromptManager:
    """
    Класс для управления промптами в системе.

    Позволяет просматривать, модифицировать и сбрасывать промпты,
    а также предоставляет интерфейс для их редактирования через Streamlit.

    Attributes:
        prompts (Dict[str, str]): Словарь оригинальных промптов
        modified_prompts (Dict[str, str]): Словарь модифицированных промптов
    """

    def __init__(self):
        # Словари для хранения оригинальных и модифицированных промптов
        self.prompts: Dict[str, str] = {}
        self.modified_prompts: Dict[str, str] = {}
        self._load_prompts()

    def _load_prompts(self):
        """
        Загружает все промпты из директории prompts.

        Читает .py файлы, извлекает строки шаблонов между тройными кавычками
        и сохраняет их в словарь prompts.
        """
        prompts_dir = "prompts"
        for file in os.listdir(prompts_dir):
            if file.endswith(".py"):
                with open(os.path.join(prompts_dir, file), "r", encoding="utf-8") as f:
                    content = f.read()
                    # Извлекаем строку шаблона между тройными кавычками
                    start = content.find('"""') + 3
                    end = content.rfind('"""')
                    if start > 2 and end > start:
                        template = content[start:end].strip()
                        prompt_name = file[:-3].upper() + "_TEMPLATE"
                        self.prompts[prompt_name] = template

    def get_prompt(self, prompt_name: str) -> Optional[str]:
        """
        Получает текущую версию промпта.

        Args:
            prompt_name (str): Имя промпта

        Returns:
            Optional[str]: Модифицированная версия промпта если существует,
                           иначе оригинальная версия
        """
        return self.modified_prompts.get(prompt_name, self.prompts.get(prompt_name))

    def modify_prompt(self, prompt_name: str, new_content: str):
        """
        Сохраняет модифицированную версию промпта.

        Args:
            prompt_name (str): Имя промпта
            new_content (str): Новое содержимое промпта
        """
        if prompt_name in self.prompts:
            self.modified_prompts[prompt_name] = new_content

    def reset_prompt(self, prompt_name: str):
        """
        Сбрасывает промпт к оригинальной версии.

        Args:
            prompt_name (str): Имя промпта для сброса
        """
        if prompt_name in self.modified_prompts:
            del self.modified_prompts[prompt_name]

    def reset_all_prompts(self):
        """Сбрасывает все промпты к их оригинальным версиям."""
        self.modified_prompts.clear()

    def render_prompt_editor(self):
        """
        Отображает интерфейс редактора промптов в Streamlit.

        Позволяет пользователю:
        - Выбрать промпт для редактирования
        - Просмотреть/изменить содержимое промпта
        - Сохранить изменения
        - Сбросить отдельный промпт или все промпты
        """
        st.subheader("Управление промптами")

        # Выбор промпта для редактирования
        prompt_names = list(self.prompts.keys())
        selected_prompt = st.selectbox(
            "Выберите промпт для просмотра/редактирования", prompt_names
        )

        if selected_prompt:
            current_prompt = self.get_prompt(selected_prompt)
            is_modified = selected_prompt in self.modified_prompts

            # Показываем статус модификации
            if is_modified:
                st.warning("⚠️ Промпт был изменен")

            # Поле для редактирования
            new_prompt = st.text_area(
                "Содержимое промпта", value=current_prompt, height=400
            )

            col1, col2, col3 = st.columns(3)

            # Кнопка сохранения изменений
            if col1.button("Сохранить изменения"):
                if new_prompt != self.prompts[selected_prompt]:
                    self.modify_prompt(selected_prompt, new_prompt)
                    st.success("✅ Изменения сохранены")
                else:
                    self.reset_prompt(selected_prompt)
                    st.info("ℹ️ Промпт вернулся к оригинальной версии")

            # Кнопка сброса текущего промпта
            if is_modified and col2.button("Сбросить этот промпт"):
                self.reset_prompt(selected_prompt)
                st.rerun()

            # Кнопка сброса всех промптов
            if self.modified_prompts and col3.button("Сбросить все промпты"):
                self.reset_all_prompts()
                st.rerun()


# Global instance
prompt_manager = PromptManager()
