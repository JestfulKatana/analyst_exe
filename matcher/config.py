#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль конфигурации для SmartJobMatcher.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class Config:
    """Класс для управления конфигурацией SmartJobMatcher."""

    DEFAULT_CONFIG = {
        "ollama": {
            "model": "llama3.2:3b",
            "url": "http://localhost:11434/api/generate",
            "timeout": 60,
            "temperature": 0.1
        },
        "scoring": {
            "weights": {
                "education_match": 25,
                "experience_match": 25,
                "hard_skills_match": 40,
                "soft_skills_match": 10
            }
        },
        "logging": {
            "level": "INFO",
            "file": "job_matcher.log",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "output": {
            "save_results": True,
            "results_dir": "results",
            "include_debug": True
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Инициализация конфигурации.

        Args:
            config_path: Путь к файлу конфигурации (JSON)
        """
        self.config_path = config_path
        self._config = self.DEFAULT_CONFIG.copy()

        if config_path:
            self.load(config_path)

    def load(self, config_path: str) -> None:
        """
        Загрузить конфигурацию из файла.

        Args:
            config_path: Путь к JSON файлу
        """
        try:
            path = Path(config_path)
            if not path.exists():
                logger.warning(f"Файл конфигурации {config_path} не найден, используются настройки по умолчанию")
                return

            with open(path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)

            # Глубокое слияние конфигураций
            self._config = self._deep_merge(self._config, user_config)
            logger.info(f"Конфигурация загружена из {config_path}")

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга конфигурации: {e}")
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")

    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """
        Глубокое слияние словарей.

        Args:
            base: Базовый словарь
            update: Словарь с обновлениями

        Returns:
            Объединённый словарь
        """
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, path: str, default: Any = None) -> Any:
        """
        Получить значение конфигурации по пути (через точку).

        Args:
            path: Путь к значению (например "ollama.model")
            default: Значение по умолчанию

        Returns:
            Значение конфигурации или default
        """
        keys = path.split('.')
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, path: str, value: Any) -> None:
        """
        Установить значение конфигурации.

        Args:
            path: Путь к значению (например "ollama.model")
            value: Новое значение
        """
        keys = path.split('.')
        config = self._config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value
        logger.debug(f"Установлено {path} = {value}")

    def save(self, output_path: Optional[str] = None) -> None:
        """
        Сохранить конфигурацию в файл.

        Args:
            output_path: Путь для сохранения (если None, используется config_path)
        """
        path = output_path or self.config_path
        if not path:
            raise ValueError("Не указан путь для сохранения конфигурации")

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            logger.info(f"Конфигурация сохранена в {path}")
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")

    @property
    def ollama_model(self) -> str:
        """Название модели Ollama."""
        return self.get("ollama.model")

    @property
    def ollama_url(self) -> str:
        """URL Ollama API."""
        return self.get("ollama.url")

    @property
    def ollama_timeout(self) -> int:
        """Таймаут для запросов к Ollama (сек)."""
        return self.get("ollama.timeout")

    @property
    def weights(self) -> Dict[str, int]:
        """Веса для скоринга."""
        return self.get("scoring.weights")

    def __repr__(self) -> str:
        return f"Config(model={self.ollama_model}, weights={self.weights})"
