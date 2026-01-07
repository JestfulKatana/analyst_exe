#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Примеры использования SmartJobMatcher
Демонстрирует различные сценарии работы с матчером
"""

from smart_job_matcher import SmartJobMatcher
import json


def example_1_basic_usage():
    """Базовый пример использования."""
    print("\n" + "="*70)
    print("ПРИМЕР 1: Базовое использование")
    print("="*70)

    job = """
    Требуется лаборант-исследователь.

    Обязанности:
    - Проведение химических анализов
    - Работа с лабораторным оборудованием
    - Ведение документации

    Требования:
    - Высшее химическое или биотехнологическое образование
    - Опыт работы от 3 лет
    - Знание MS Office (Word, Excel)
    - Коммуникабельность, ответственность
    """

    resume = """
    Образование: МГУ, факультет биотехнологии
    Опыт: 2.5 года в фармацевтической лаборатории
    Навыки: хроматография, спектрофотометрия, MS Office
    Личные качества: ответственный, коммуникабельный
    """

    matcher = SmartJobMatcher()
    result = matcher.match(job, resume)

    print(f"\n🎯 Итоговый скор: {result['score']}/100")
    print(f"\n💬 Фидбэк:\n{result['feedback']}")
    print(f"\n✅ Сильные стороны:")
    for item in result['report']['strengths'][:5]:
        print(f"   {item}")

    if result['report']['missing_required']:
        print(f"\n❌ Что не хватает:")
        for item in result['report']['missing_required'][:5]:
            print(f"   {item}")


def example_2_perfect_match():
    """Пример с идеальным совпадением."""
    print("\n" + "="*70)
    print("ПРИМЕР 2: Идеальное совпадение")
    print("="*70)

    job = """
    Python Backend разработчик.

    Требования:
    - Опыт: от 2 лет
    - Python 3.8+, FastAPI, PostgreSQL
    - Docker, Git
    - Высшее техническое образование
    - Командная работа, самостоятельность
    """

    resume = """
    Образование: МФТИ, прикладная математика
    Опыт: 3 года Python разработки
    Стек: Python, FastAPI, PostgreSQL, Docker, Git, pytest
    Качества: люблю командную работу, самостоятельный
    """

    matcher = SmartJobMatcher()
    result = matcher.match(job, resume)

    print(f"\n🎯 Итоговый скор: {result['score']}/100")
    print(f"\n💬 {result['feedback']}")


def example_3_poor_match():
    """Пример с плохим совпадением."""
    print("\n" + "="*70)
    print("ПРИМЕР 3: Слабое совпадение")
    print("="*70)

    job = """
    Senior DevOps Engineer.

    Требования:
    - Опыт: от 5 лет в DevOps
    - Kubernetes, Terraform, AWS
    - CI/CD: Jenkins, GitLab CI
    - Python/Bash скриптинг
    - Высшее техническое
    """

    resume = """
    Образование: среднее специальное
    Опыт: 1 год junior frontend разработчиком
    Навыки: HTML, CSS, JavaScript, React
    """

    matcher = SmartJobMatcher()
    result = matcher.match(job, resume)

    print(f"\n🎯 Итоговый скор: {result['score']}/100")
    print(f"\n💬 {result['feedback']}")
    print(f"\n❌ Отсутствующие требования:")
    for item in result['report']['missing_required'][:8]:
        print(f"   {item}")


def example_4_save_results():
    """Пример с сохранением результатов."""
    print("\n" + "="*70)
    print("ПРИМЕР 4: Сохранение результатов")
    print("="*70)

    job = "Data Scientist. Требования: Python, ML, SQL, опыт 2+ года"
    resume = "Python разработчик, 3 года. Навыки: Python, scikit-learn, pandas, SQL"

    matcher = SmartJobMatcher()
    result = matcher.match(job, resume)

    # Сохранение в файл
    filepath = matcher.save_result(result, "example_result.json")
    print(f"\n💾 Результат сохранён в: {filepath}")

    # Чтение обратно
    with open(filepath, 'r', encoding='utf-8') as f:
        loaded_result = json.load(f)

    print(f"📖 Загружен скор: {loaded_result['score']}/100")


def example_5_batch_processing():
    """Пример пакетной обработки."""
    print("\n" + "="*70)
    print("ПРИМЕР 5: Пакетная обработка")
    print("="*70)

    jobs = [
        "Python разработчик, Django, PostgreSQL, опыт 3+ года",
        "Frontend разработчик, React, TypeScript, опыт 2+ года",
        "DevOps инженер, Kubernetes, Docker, AWS, опыт 4+ года"
    ]

    candidate_resume = """
    Fullstack разработчик, 3 года опыта.
    Backend: Python, Django, FastAPI, PostgreSQL
    Frontend: React, JavaScript, HTML/CSS
    DevOps: Docker, базовые знания Kubernetes
    """

    matcher = SmartJobMatcher()

    results = []
    for i, job in enumerate(jobs, 1):
        print(f"\nАнализ вакансии {i}/3...")
        result = matcher.match(job, candidate_resume, generate_feedback=False)
        results.append({
            'job_id': i,
            'score': result['score'],
            'job_preview': job[:50] + "..."
        })

    # Сортировка по убыванию скора
    results.sort(key=lambda x: x['score'], reverse=True)

    print("\n📊 Результаты (отсортированы по совместимости):")
    for r in results:
        print(f"   Вакансия {r['job_id']}: {r['score']}/100 - {r['job_preview']}")


def example_6_custom_weights():
    """Пример с кастомными весами."""
    print("\n" + "="*70)
    print("ПРИМЕР 6: Настройка весов под стажёра")
    print("="*70)

    job = """
    Стажёр-аналитик данных.
    Требования: студент/выпускник технического вуза,
    знание Python и SQL, желание учиться.
    """

    resume = """
    Студент 4 курса МФТИ.
    Навыки: Python, SQL, базовые знания pandas.
    Мотивированный, быстро обучаюсь.
    """

    # Для стажёра важнее образование и soft skills, опыт не критичен
    matcher = SmartJobMatcher()
    matcher.weights = {
        'education_match': 40,      # Повысили
        'experience_match': 10,      # Понизили
        'hard_skills_match': 35,
        'soft_skills_match': 15      # Повысили
    }

    result = matcher.match(job, resume)
    print(f"\n🎯 Скор с приоритетом на образование: {result['score']}/100")
    print(f"💬 {result['feedback']}")


def main():
    """Запуск всех примеров."""
    print("\n" + "="*70)
    print("🚀 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ SmartJobMatcher")
    print("="*70)
    print("\n⚠️  Убедитесь что Ollama запущен:")
    print("   $ ollama serve")
    print("   $ ollama pull llama3.2:3b")
    print("\n" + "="*70)

    try:
        # Запуск примеров
        example_1_basic_usage()
        example_2_perfect_match()
        example_3_poor_match()
        example_4_save_results()
        example_5_batch_processing()
        example_6_custom_weights()

        print("\n" + "="*70)
        print("✅ Все примеры успешно выполнены!")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\nПроверьте что:")
        print("1. Ollama запущен (ollama serve)")
        print("2. Модель загружена (ollama pull llama3.2:3b)")
        print("3. Установлены зависимости (pip install -r requirements.txt)")


if __name__ == "__main__":
    main()
