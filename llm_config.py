import os

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(override=True)

# OpenRouter model mappings
OPENROUTER_BASE_CONFIG = {
    "api_key": st.secrets.get("OPENROUTER_API_KEY", ""),
    "base_url": "https://openrouter.ai/api/v1",
}

LLM_CONFIG = {
    "DeepSeek R1": {
        "model": "deepseek/deepseek-r1:free",
        **OPENROUTER_BASE_CONFIG,
    },
    "DeepSeek Chat": {
        "model": "deepseek/deepseek-chat:free", 
        **OPENROUTER_BASE_CONFIG,
    },
    "Gemini 2.0 Pro": {
        "model": "google/gemini-2.0-pro-exp-02-05:free",
        **OPENROUTER_BASE_CONFIG,
    },
    "Llama 3.3 70B Instruct": {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        **OPENROUTER_BASE_CONFIG,
    },
    "Gemini 2.0 Flash": {
        "model": "google/gemini-2.0-flash-exp:free",
        **OPENROUTER_BASE_CONFIG,
    },
    "Qwen 32B": {
        "model": "qwen/qwq-32b:free",
        **OPENROUTER_BASE_CONFIG,
    },
    "Gemma 3 27B": {
        "model": "google/gemma-3-27b-it:free",
        **OPENROUTER_BASE_CONFIG,
    },
    "Qwen 2.5 72B": {
        "model": "qwen/qwen-2.5-72b-instruct:free",
        **OPENROUTER_BASE_CONFIG,
    },
    "Mistral Small 24B": {
        "model": "mistralai/mistral-small-24b-instruct:free",
        **OPENROUTER_BASE_CONFIG,
    },
    "Reka Flash 3": {
        "model": "rekaai/reka-flash-3:free",
        **OPENROUTER_BASE_CONFIG,
    },
}

LLM_CLASSES = {model: ChatOpenAI for model in LLM_CONFIG.keys()}


def get_llm():
    """
    Выбор и создание экземпляра LLM-модели на основе выбора пользователя,
    хранящегося в состоянии сессии.

    Эта функция извлекает выбор пользователя модели LLM из состояния сессии
    Streamlit. Затем она получает соответствующую конфигурацию и класс для
    выбранной модели из предопределенных словарей. Если инициализация модели
    не удалась, она регистрирует сообщение об ошибке и возвращает None.

    Возвращает:
        Экземпляр выбранного класса LLM-модели или None, если инициализация
        не удалась.
    """
    if not st.secrets.get("OPENROUTER_API_KEY"):
        st.error("⚠️ OPENROUTER_API_KEY не найден в secrets. Пожалуйста, добавьте его в .streamlit/secrets.toml")
        return None

    llm_choice = st.session_state.get("llm_choice", "DeepSeek Chat")
    config = LLM_CONFIG.get(llm_choice, LLM_CONFIG["DeepSeek Chat"])
    llm_class = LLM_CLASSES.get(llm_choice, ChatOpenAI)

    try:
        return llm_class(
            model=config["model"],
            api_key=config["api_key"],
            base_url=config["base_url"],
            temperature=0,
        )
    except Exception as e:
        st.error(f"Ошибка при инициализации LLM: {e}")
        return None
