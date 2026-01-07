#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartJobMatcher - Умный матчер вакансий и резюме на основе LLM.

DEPRECATED: Этот файл оставлен для обратной совместимости.
Используйте вместо этого: from matcher import SmartJobMatcher, Config
"""

import logging
from matcher import SmartJobMatcher, Config

# Настройка логирования для обратной совместимости
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_matcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Для обратной совместимости экспортируем класс
__all__ = ['SmartJobMatcher', 'Config']


# Старый код ниже (закомментирован, оставлен для истории)
"""
class SmartJobMatcher_OLD:
    """
    Класс для интеллектуального сопоставления вакансий и резюме.

    Использует LLM (через Ollama) для парсинга текста и собственный
    детерминированный алгоритм для расчёта совместимости.
    """

    def __init__(
        self,
        ollama_model: str = "llama3.2:3b",
        ollama_url: str = "http://localhost:11434/api/generate",
        timeout: int = 60
    ):
        """
        Инициализация матчера.

        Args:
            ollama_model: Название модели Ollama
            ollama_url: URL Ollama API
            timeout: Таймаут для запросов к LLM (сек)
        """
        self.ollama_url = ollama_url
        self.ollama_model = ollama_model
        self.timeout = timeout

        # Настройки весов для скоринга
        self.weights = {
            'education_match': 25,
            'experience_match': 25,
            'hard_skills_match': 40,  # Будет распределено на количество навыков
            'soft_skills_match': 10,
        }

        logger.info(f"Инициализирован SmartJobMatcher с моделью {ollama_model}")

        # Проверка доступности Ollama
        self._check_ollama_availability()

    def _check_ollama_availability(self) -> bool:
        """Проверка доступности Ollama сервера."""
        try:
            response = requests.get(
                self.ollama_url.replace('/api/generate', '/api/tags'),
                timeout=5
            )
            if response.status_code == 200:
                logger.info("✓ Ollama сервер доступен")
                return True
            else:
                logger.warning(f"⚠ Ollama сервер вернул статус {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Ollama сервер недоступен: {e}")
            logger.error("Убедитесь, что Ollama запущен: ollama serve")
            return False

    def _query_llm(self, prompt: str) -> str:
        """
        Универсальный метод для запроса к LLM через Ollama.

        Args:
            prompt: Текст запроса

        Returns:
            Ответ от LLM в формате JSON строки
        """
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1  # Минимум случайности
            }
        }

        try:
            logger.debug(f"Отправка запроса к LLM (длина промпта: {len(prompt)} символов)")
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json().get('response', '{}')
            logger.debug(f"Получен ответ от LLM (длина: {len(result)} символов)")
            return result

        except requests.exceptions.Timeout:
            logger.error(f"Таймаут при запросе к LLM (>{self.timeout}с)")
            return "{}"
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к LLM: {e}")
            return "{}"
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе к LLM: {e}")
            return "{}"

    def _parse_text_with_llm(self, text: str, is_job: bool = True) -> Dict[str, Any]:
        """
        Использует LLM для извлечения структурированной информации из текста.

        Args:
            text: Текст вакансии или резюме
            is_job: True для вакансии, False для резюме

        Returns:
            Словарь с распарсенными данными
        """
        doc_type = "вакансии" if is_job else "резюме кандидата"

        prompt = f"""
Ты — эксперт по анализу HR-документов. Твоя задача — извлечь структурированную информацию из текста {doc_type}.

Проанализируй текст и верни ТОЛЬКО JSON в следующем формате:
{{
    "education": "Строка с описанием требуемого/имеющегося образования. Если не указано, верни пустую строку.",
    "experience_years": ЧИСЛО (минимальный требуемый или фактический опыт в годах). Если не указано, верни 0,
    "hard_skills": ["навык1", "навык2", ...], // Список всех упомянутых технических навыков, технологий, оборудования, методик, ПО
    "soft_skills": ["качество1", "качество2", ...] // Список всех упомянутых личностных качеств
}}

Текст:
{text}

Помни: твоя цель — точность и полнота, а не выдумывание. Если информации нет — оставляй поле пустым.
"""

        try:
            raw_response = self._query_llm(prompt)
            parsed_data = json.loads(raw_response)

            # Валидация структуры
            required_fields = ['education', 'experience_years', 'hard_skills', 'soft_skills']
            for field in required_fields:
                if field not in parsed_data:
                    logger.warning(f"Отсутствует поле '{field}' в ответе LLM, добавляю значение по умолчанию")
                    if field == 'experience_years':
                        parsed_data[field] = 0
                    elif 'skills' in field:
                        parsed_data[field] = []
                    else:
                        parsed_data[field] = ""

            logger.info(f"Успешно распарсен {doc_type}")
            return parsed_data

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON от LLM: {e}")
            logger.debug(f"Сырой ответ: {raw_response[:200]}...")
            return self._get_empty_parsed_data()
        except Exception as e:
            logger.error(f"Ошибка при парсинге текста: {e}")
            return self._get_empty_parsed_data()

    def _get_empty_parsed_data(self) -> Dict[str, Any]:
        """Возвращает пустую структуру данных для fallback."""
        return {
            "education": "",
            "experience_years": 0,
            "hard_skills": [],
            "soft_skills": []
        }

    def _calculate_score(
        self,
        job_data: Dict[str, Any],
        resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Детерминированный алгоритм расчёта скоринга на основе структурированных данных.

        Args:
            job_data: Распарсенные данные вакансии
            resume_data: Распарсенные данные резюме

        Returns:
            Словарь с итоговым скором и детальным отчётом
        """
        report = {
            "missing_required": [],
            "partial_match": [],
            "strengths": [],
            "score_details": {}
        }
        total_score = 0

        # --- 1. Образование ---
        edu_score = self.weights['education_match'] if job_data['education'] and resume_data['education'] else 0
        report['score_details']['education'] = edu_score

        if edu_score > 0:
            report['strengths'].append("Релевантное образование")
        else:
            if job_data['education']:
                report['missing_required'].append("Релевантное образование")

        total_score += edu_score

        # --- 2. Опыт ---
        job_exp = job_data['experience_years']
        resume_exp = resume_data['experience_years']
        exp_score = 0

        if job_exp > 0:
            if resume_exp >= job_exp:
                exp_score = self.weights['experience_match']
                report['strengths'].append(f"Опыт: {resume_exp} лет (требуется {job_exp})")
            elif resume_exp > 0:
                exp_score = (resume_exp / job_exp) * self.weights['experience_match']
                report['partial_match'].append(f"Опыт: {resume_exp} лет (требуется {job_exp})")
            else:
                report['missing_required'].append(f"Опыт работы {job_exp} лет")

        report['score_details']['experience'] = round(exp_score, 2)
        total_score += exp_score

        # --- 3. Hard Skills ---
        job_skills = set(s.lower().strip() for s in job_data['hard_skills'])
        resume_skills = set(s.lower().strip() for s in resume_data['hard_skills'])

        if job_skills:
            matched_skills = job_skills & resume_skills
            missing_skills = job_skills - resume_skills

            # Распределяем вес поровну на каждый обязательный навык
            points_per_skill = self.weights['hard_skills_match'] / len(job_skills)
            hs_score = len(matched_skills) * points_per_skill

            report['score_details']['hard_skills'] = round(hs_score, 2)
            total_score += hs_score

            if matched_skills:
                report['strengths'].extend(f"✓ {skill}" for skill in matched_skills)
            if missing_skills:
                report['missing_required'].extend(f"✗ {skill}" for skill in missing_skills)
        else:
            report['score_details']['hard_skills'] = 0

        # --- 4. Soft Skills ---
        job_soft = set(s.lower().strip() for s in job_data['soft_skills'])
        resume_soft = set(s.lower().strip() for s in resume_data['soft_skills'])
        matched_soft = job_soft & resume_soft

        ss_score = len(matched_soft) * (self.weights['soft_skills_match'] / max(1, len(job_soft))) if job_soft else 0

        report['score_details']['soft_skills'] = round(ss_score, 2)
        total_score += ss_score

        if matched_soft:
            report['strengths'].extend(f"+ {skill}" for skill in matched_soft)

        # Нормализуем до 0-100
        final_score = min(100, round(total_score))

        logger.info(f"Рассчитан итоговый скор: {final_score}/100")

        return {
            'score': final_score,
            'report': report
        }

    def _generate_human_feedback(self, report: Dict[str, Any], score: int) -> str:
        """
        Генерирует дружелюбный фидбэк для пользователя на основе структурированного отчёта.

        Args:
            report: Отчёт с деталями соответствия
            score: Итоговый скор

        Returns:
            Текстовый фидбэк
        """
        prompt = f"""
На основе этого технического отчёта о соответствии кандидата вакансии, напиши краткий, конструктивный и поддерживающий фидбэк на русском языке.

Итоговый скор: {score}/100

Отчёт:
- Сильные стороны: {report['strengths'][:5]}
- Частичные совпадения: {report['partial_match']}
- Отсутствующие обязательные навыки: {report['missing_required'][:5]}

Правила:
1. Пиши в 3-4 предложения.
2. Не упоминай проценты или баллы напрямую.
3. Дай рекомендацию: стоит ли откликаться?
4. Сохрани нейтральный, но дружелюбный тон.
5. Верни ТОЛЬКО текст фидбэка без JSON и кавычек.
"""

        try:
            raw_feedback = self._query_llm(prompt)
            # Пытаемся извлечь текст из JSON если LLM вернул JSON
            try:
                parsed = json.loads(raw_feedback)
                if isinstance(parsed, dict) and 'feedback' in parsed:
                    return parsed['feedback'].strip()
                elif isinstance(parsed, str):
                    return parsed.strip()
            except:
                pass

            # Если не JSON, возвращаем как есть
            feedback = raw_feedback.strip('"\n ')
            return feedback if feedback else self._get_default_feedback(score)

        except Exception as e:
            logger.error(f"Ошибка при генерации фидбэка: {e}")
            return self._get_default_feedback(score)

    def _get_default_feedback(self, score: int) -> str:
        """Генерирует стандартный фидбэк на основе скора."""
        if score >= 80:
            return "Отличное соответствие! Ваш профиль хорошо подходит под требования вакансии. Рекомендуем откликнуться."
        elif score >= 60:
            return "Хорошее соответствие. Есть несколько областей для развития, но в целом профиль релевантен. Стоит откликнуться."
        elif score >= 40:
            return "Частичное соответствие. Рекомендуем усилить профиль недостающими навыками перед откликом."
        else:
            return "Низкое соответствие. Возможно, стоит рассмотреть другие вакансии или дополнить свои компетенции."

    def match(
        self,
        job_description: str,
        resume_text: str,
        generate_feedback: bool = True
    ) -> Dict[str, Any]:
        """
        Основной метод для сопоставления вакансии и резюме.

        Args:
            job_description: Текст описания вакансии
            resume_text: Текст резюме
            generate_feedback: Генерировать ли текстовый фидбэк

        Returns:
            Словарь с результатами анализа
        """
        logger.info("="*60)
        logger.info("Начало анализа совместимости")
        logger.info("="*60)

        try:
            # Парсинг вакансии
            logger.info("📋 Парсинг вакансии с помощью LLM...")
            job_data = self._parse_text_with_llm(job_description, is_job=True)

            # Парсинг резюме
            logger.info("👤 Парсинг резюме с помощью LLM...")
            resume_data = self._parse_text_with_llm(resume_text, is_job=False)

            # Расчёт соответствия
            logger.info("🔢 Расчёт соответствия...")
            result = self._calculate_score(job_data, resume_data)

            # Генерация фидбэка
            if generate_feedback:
                logger.info("💬 Генерация фидбэка...")
                result['feedback'] = self._generate_human_feedback(
                    result['report'],
                    result['score']
                )

            # Добавляем отладочную информацию
            result['debug'] = {
                'parsed_job': job_data,
                'parsed_resume': resume_data,
                'timestamp': datetime.now().isoformat()
            }

            logger.info("✓ Анализ завершён успешно")
            return result

        except Exception as e:
            logger.error(f"Критическая ошибка при анализе: {e}", exc_info=True)
            return {
                'score': 0,
                'report': {
                    'missing_required': [],
                    'partial_match': [],
                    'strengths': [],
                    'score_details': {}
                },
                'feedback': "Произошла ошибка при анализе. Проверьте логи.",
                'error': str(e)
            }

    def save_result(self, result: Dict[str, Any], filepath: str = None) -> str:
        """
        Сохраняет результат анализа в JSON файл.

        Args:
            result: Результат анализа
            filepath: Путь для сохранения (если None, генерируется автоматически)

        Returns:
            Путь к сохранённому файлу
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"match_result_{timestamp}.json"

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"Результат сохранён в {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Ошибка при сохранении результата: {e}")
            raise


"""


def main():
    """Демонстрация работы SmartJobMatcher."""

    # Пример вакансии
    job = """
    Обязанности:
    Самостоятельно осваивает новые и используемые в лаборатории методики.
    Проводит лабораторные анализы, испытания и другие виды исследований.
    Ведет документацию: протоколы испытаний, рабочие журналы, отчеты.
    Следит за правильной эксплуатацией лабораторного оборудования.

    Требования:
    Образование: высшее профессиональное (химическое, биотехнологическое).
    Опыт работы: от 3 лет.
    Уверенное владение компьютером (Word, Excel).
    Личностные качества: коммуникабельность, быстрая обучаемость.
    Необходимо знать: оборудование лаборатории, стандарты, технологию производства.
    """

    # Пример резюме
    resume = """
    Образование: МГУ, специальность "Биотехнология".
    Опыт: 2 года 6 месяцев в лаборатории ПАО "ФармСинтез".
    Навыки: Работа с хроматографами и спектрофотометрами, оформление протоколов по ГОСТ,
    опыт валидации методик, знание основ производства лекарственных средств.
    Владение ПК: Уверенный пользователь MS Office (Word, Excel, PowerPoint).
    Дополнительно: Ответственный, легко осваиваю новые методики, коммуникабельный.
    """

    # Инициализация и запуск
    print("🚀 Запуск SmartJobMatcher...")
    print("⚠️  Убедитесь, что Ollama запущен: ollama serve")
    print("⚠️  И модель загружена: ollama pull llama3.2:3b\n")

    # Загрузка конфигурации
    config = Config("config.json")
    matcher = SmartJobMatcher(config=config)
    result = matcher.match(job, resume)

    # Вывод результатов
    print("\n" + "="*60)
    print(f"🎯 ИТОГОВЫЙ СКОР: {result['score']}/100")
    print("="*60)

    if 'feedback' in result:
        print(f"\n💬 Фидбэк:\n{result['feedback']}\n")

    print("\n📊 Детали оценки:")
    for category, score in result['report']['score_details'].items():
        print(f"  • {category}: {score}")

    print("\n✅ Сильные стороны:")
    for item in result['report']['strengths'][:10]:
        print(f"  {item}")

    if result['report']['missing_required']:
        print("\n❌ Отсутствующие требования:")
        for item in result['report']['missing_required'][:10]:
            print(f"  {item}")

    # Сохранение результата
    saved_path = matcher.save_result(result)
    print(f"\n💾 Результат сохранён: {saved_path}")


if __name__ == "__main__":
    main()
