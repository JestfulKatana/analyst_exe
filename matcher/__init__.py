"""
Matcher - умный матчер вакансий и резюме на основе LLM.

Основные компоненты:
- SmartJobMatcher: класс для анализа совместимости вакансий и резюме
- Config: загрузка и управление конфигурацией
"""

from .core import SmartJobMatcher
from .config import Config

__version__ = "1.0.0"
__all__ = ["SmartJobMatcher", "Config"]
