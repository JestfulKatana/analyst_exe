#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование SmartJobMatcher на примерах данных из sample_data.json
"""

import sys
import json
from pathlib import Path

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from smart_job_matcher import SmartJobMatcher


def load_sample_data():
    """Загрузка примеров данных."""
    data_file = Path(__file__).parent / "sample_data.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_single_match(matcher, job, resume):
    """Тестирование одного совпадения."""
    print(f"\n{'='*70}")
    print(f"🔍 Сравнение:")
    print(f"   Вакансия: {job['title']}")
    print(f"   Кандидат: {resume['name']}")
    print(f"{'='*70}")

    result = matcher.match(job['description'], resume['text'])

    print(f"\n🎯 Скор: {result['score']}/100")
    print(f"\n💬 Фидбэк:\n{result['feedback']}")

    # Детали
    print(f"\n📊 Детализация:")
    for category, score in result['report']['score_details'].items():
        print(f"   {category:20s}: {score:5.1f}")

    # Сильные стороны
    if result['report']['strengths']:
        print(f"\n✅ Сильные стороны:")
        for item in result['report']['strengths'][:5]:
            print(f"   {item}")

    # Что не хватает
    if result['report']['missing_required']:
        print(f"\n❌ Не хватает:")
        for item in result['report']['missing_required'][:5]:
            print(f"   {item}")

    return result


def test_all_combinations(matcher, data):
    """Тестирование всех комбинаций вакансий и резюме."""
    print(f"\n{'='*70}")
    print("📊 МАТРИЦА СОВМЕСТИМОСТИ")
    print(f"{'='*70}\n")

    results_matrix = []

    for job in data['jobs']:
        job_results = []
        for resume in data['resumes']:
            result = matcher.match(
                job['description'],
                resume['text'],
                generate_feedback=False  # Отключаем для скорости
            )
            job_results.append(result['score'])

        results_matrix.append(job_results)

    # Вывод таблицы
    print(f"{'Вакансия':<30} | ", end="")
    for resume in data['resumes']:
        print(f"{resume['name']:<15} | ", end="")
    print()
    print("-" * 120)

    for i, job in enumerate(data['jobs']):
        print(f"{job['title']:<30} | ", end="")
        for score in results_matrix[i]:
            # Цветовое кодирование
            if score >= 70:
                marker = "🟢"
            elif score >= 50:
                marker = "🟡"
            else:
                marker = "🔴"
            print(f"{marker} {score:>3}/100      | ", end="")
        print()

    print("\n🟢 - Отличное совпадение (70+)")
    print("🟡 - Среднее совпадение (50-69)")
    print("🔴 - Слабое совпадение (<50)")

    # Лучшие матчи
    print(f"\n{'='*70}")
    print("🏆 ТОП-3 ЛУЧШИХ СОВПАДЕНИЙ")
    print(f"{'='*70}\n")

    all_matches = []
    for i, job in enumerate(data['jobs']):
        for j, resume in enumerate(data['resumes']):
            all_matches.append({
                'job': job['title'],
                'resume': resume['name'],
                'score': results_matrix[i][j]
            })

    all_matches.sort(key=lambda x: x['score'], reverse=True)

    for idx, match in enumerate(all_matches[:3], 1):
        print(f"{idx}. {match['job']} ⟷ {match['resume']}")
        print(f"   Скор: {match['score']}/100\n")


def main():
    """Основная функция."""
    print("\n" + "="*70)
    print("🧪 ТЕСТИРОВАНИЕ SmartJobMatcher НА ПРИМЕРАХ ДАННЫХ")
    print("="*70)

    # Загрузка данных
    data = load_sample_data()
    print(f"\n✓ Загружено {len(data['jobs'])} вакансий и {len(data['resumes'])} резюме")

    # Инициализация матчера
    matcher = SmartJobMatcher()

    # Режим работы
    print("\nВыберите режим:")
    print("1. Детальный анализ одной пары")
    print("2. Матрица совместимости всех комбинаций")
    print("3. Оба режима")

    try:
        choice = input("\nВаш выбор (1/2/3): ").strip()
    except (EOFError, KeyboardInterrupt):
        choice = "2"  # По умолчанию матрица
        print("2")

    if choice in ["1", "3"]:
        # Детальный анализ
        print("\nДоступные вакансии:")
        for i, job in enumerate(data['jobs']):
            print(f"{i+1}. {job['title']}")

        print("\nДоступные резюме:")
        for i, resume in enumerate(data['resumes']):
            print(f"{i+1}. {resume['name']}")

        try:
            job_idx = int(input("\nНомер вакансии: ")) - 1
            resume_idx = int(input("Номер резюме: ")) - 1
        except (ValueError, EOFError, KeyboardInterrupt):
            # По умолчанию первые
            job_idx, resume_idx = 0, 0
            print("1")
            print("1")

        test_single_match(
            matcher,
            data['jobs'][job_idx],
            data['resumes'][resume_idx]
        )

    if choice in ["2", "3"]:
        # Матрица всех комбинаций
        test_all_combinations(matcher, data)

    print("\n" + "="*70)
    print("✅ Тестирование завершено!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
