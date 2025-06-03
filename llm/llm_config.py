import logging
import random
from typing import Any, Dict, Optional, Type, Union

import streamlit as st
from dotenv import load_dotenv
from langchain_community.llms import YandexGPT
from langchain_gigachat import GigaChat
from langchain_openai import ChatOpenAI

# Загрузка переменных окружения
load_dotenv(override=True)


class LLMConfig:
    """Класс для управления конфигурациями LLM моделей."""

    @staticmethod
    def get_openrouter_base_config() -> Dict[str, str]:
        """Возвращает базовую конфигурацию для OpenRouter."""

        openrouter_random_key_number = random.randint(1, 16)

        return {
            "api_key": st.secrets.get(
                f"OPENROUTER_API_KEY_{openrouter_random_key_number}", ""
            ),
            "base_url": "https://openrouter.ai/api/v1",
        }

    @staticmethod
    def get_yandex_config() -> Dict[str, str]:
        """Возвращает конфигурацию для YandexGPT."""
        return {
            "api_key": st.secrets.get("YANDEX_API_KEY", ""),
            "folder_id": st.secrets.get("YANDEX_FOLDER_ID", ""),
        }

    @staticmethod
    def get_gigachat_config() -> Dict[str, str]:
        """Возвращает конфигурацию для GigaChat."""
        return {
            "api_key": st.secrets.get("GIGACHAT_CREDENTIALS", ""),
            "scope": st.secrets.get("GIGACHAT_API_PERS", ""),
        }

    @classmethod
    def get_model_configs(cls) -> Dict[str, Dict[str, Any]]:
        """Возвращает конфигурации для всех поддерживаемых моделей."""
        openrouter_config = cls.get_openrouter_base_config()
        yandex_config = cls.get_yandex_config()
        gigachat_config = cls.get_gigachat_config()

        return {
            # Российские модели
            "YandexGPT Pro": {
                "model_uri": f"gpt://{yandex_config['folder_id']}/yandexgpt/latest",
                **yandex_config,
            },
            "YandexGPT Lite": {
                "model_uri": f"gpt://{yandex_config['folder_id']}/yandexgpt-lite/latest",
                **yandex_config,
            },
            "GigaChat": {
                "model": "GigaChat",
                **gigachat_config,
            },
            # Модели через OpenRouter
            "DeepSeek R1": {
                "model": "deepseek/deepseek-r1:free",
                **openrouter_config,
            },
            "DeepSeek Chat": {
                "model": "deepseek/deepseek-chat-v3-0324:free",
                **openrouter_config,
            },
            "Gemini 2.0 Pro": {
                "model": "google/gemini-2.0-pro-exp-02-05:free",
                **openrouter_config,
            },
            "Llama 3.3 70B Instruct": {
                "model": "meta-llama/llama-3.3-70b-instruct:free",
                **openrouter_config,
            },
            "Gemini 2.0 Flash": {
                "model": "google/gemini-2.0-flash-exp:free",
                **openrouter_config,
            },
            "Gemini 2.5 Pro": {
                "model": "google/gemini-2.5-pro-exp-03-25:free",
                **openrouter_config,
            },
            "Qwen 32B": {
                "model": "qwen/qwq-32b:free",
                **openrouter_config,
            },
            "Gemma 3 27B": {
                "model": "google/gemma-3-27b-it:free",
                **openrouter_config,
            },
            "Qwen 2.5 72B": {
                "model": "qwen/qwen2.5-vl-72b-instruct:free",
                **openrouter_config,
            },
            "Mistral Small 24B": {
                "model": "mistralai/mistral-small-24b-instruct-2501:free",
                **openrouter_config,
            },
            "Reka Flash 3": {
                "model": "rekaai/reka-flash-3:free",
                **openrouter_config,
            },
        }


class LLMFactory:
    """Класс для создания экземпляров LLM моделей."""

    @staticmethod
    def get_llm_classes() -> Dict[str, Type[Union[YandexGPT, GigaChat, ChatOpenAI]]]:
        """Возвращает словарь соответствия названий моделей и их классов."""
        return {
            "YandexGPT Pro": YandexGPT,
            "YandexGPT Lite": YandexGPT,
            "GigaChat": GigaChat,
            **{
                model: ChatOpenAI
                for model in LLMConfig.get_model_configs().keys()
                if model not in ["YandexGPT Lite", "YandexGPT Pro", "GigaChat"]
            },
        }

    @classmethod
    def create_llm(cls, model_name: str = "DeepSeek Chat") -> Optional[Any]:
        """
        Создает экземпляр LLM модели на основе выбора пользователя.

        Args:
            model_name: Название модели для создания.

        Returns:
            Экземпляр LLM модели или None в случае ошибки.
        """
        # Проверяем наличие необходимых ключей API в зависимости от модели
        if model_name in ["YandexGPT Lite", "YandexGPT Pro"]:
            if not st.secrets.get("YANDEX_API_KEY") or not st.secrets.get(
                "YANDEX_FOLDER_ID"
            ):
                logging.error(
                    "⚠️ Отсутствуют YANDEX_API_KEY или YANDEX_FOLDER_ID в secrets"
                )
                raise ValueError(
                    "Отсутствуют YANDEX_API_KEY или YANDEX_FOLDER_ID в secrets"
                )
        elif model_name == "GigaChat":
            if not st.secrets.get("GIGACHAT_CREDENTIALS") or not st.secrets.get(
                "GIGACHAT_API_PERS"
            ):
                logging.error(
                    "⚠️ Отсутствуют GIGACHAT_CREDENTIALS или GIGACHAT_API_PERS в secrets"
                )
                raise ValueError(
                    "Отсутствуют GIGACHAT_CREDENTIALS или GIGACHAT_API_PERS в secrets"
                )

        model_configs = LLMConfig.get_model_configs()
        llm_classes = cls.get_llm_classes()

        config = model_configs.get(model_name, model_configs["DeepSeek Chat"])
        llm_class = llm_classes.get(model_name, ChatOpenAI)

        try:
            if llm_class.__name__ == "ChatOpenAI":
                return llm_class(
                    model=config["model"],
                    api_key=config["api_key"],
                    base_url=config["base_url"],
                    temperature=0,
                )
            elif llm_class.__name__ == "YandexGPT":
                return llm_class(
                    model_uri=config["model_uri"],
                    api_key=config["api_key"],
                    folder_id=config["folder_id"],
                    temperature=0,
                )
            elif llm_class.__name__ == "GigaChat":
                return llm_class(
                    model=config["model"],
                    access_token=config["api_key"],
                    scope=config["scope"],
                    temperature=0,
                    verify_ssl_certs=False,
                )
        except Exception as e:
            logging.error(f"Ошибка при инициализации LLM: {e}")
            raise e


def get_llm() -> Optional[Any]:
    """
    Создает экземпляр LLM модели на основе выбора пользователя.

    Returns:
        Экземпляр LLM модели или None в случае ошибки.
    """
    llm_choice = st.session_state.get("llm_choice", "DeepSeek Chat")
    return LLMFactory.create_llm(llm_choice)
