# Matcher - Модуль умного сопоставления вакансий и резюме

Профессиональный Python пакет для анализа совместимости вакансий и резюме с использованием LLM.

## Архитектура

```
matcher/
├── __init__.py       # Экспорт основных классов
├── core.py          # SmartJobMatcher - основной класс
├── config.py        # Config - управление конфигурацией
└── README.md        # Документация модуля
```

## Установка

```python
# Как модуль
from matcher import SmartJobMatcher, Config

# Для обратной совместимости
from smart_job_matcher import SmartJobMatcher
```

## Быстрый старт

### Базовое использование

```python
from matcher import SmartJobMatcher

# Самый простой способ (настройки по умолчанию)
matcher = SmartJobMatcher()

job = "Python разработчик, опыт 3+ года, Django, PostgreSQL"
resume = "Python разработчик, 4 года опыта. Django, PostgreSQL, Redis"

result = matcher.match(job, resume)
print(f"Совместимость: {result['score']}/100")
print(f"Фидбэк: {result['feedback']}")
```

### С конфигурационным файлом

```python
from matcher import SmartJobMatcher, Config

# Загрузка конфигурации из файла
config = Config("config.json")
matcher = SmartJobMatcher(config=config)

result = matcher.match(job_text, resume_text)
```

### Переопределение параметров

```python
from matcher import SmartJobMatcher, Config

# Загрузка базовой конфигурации
config = Config("config.json")

# Переопределение конкретных параметров
matcher = SmartJobMatcher(
    config=config,
    ollama_model="llama3.2:1b",  # Более лёгкая модель
    timeout=120                   # Увеличенный таймаут
)
```

### Настройка весов в runtime

```python
matcher = SmartJobMatcher()

# Для стажёра: образование важнее опыта
matcher.weights = {
    'education_match': 40,
    'experience_match': 10,
    'hard_skills_match': 35,
    'soft_skills_match': 15
}

result = matcher.match(job, resume)
```

## API Reference

### SmartJobMatcher

Основной класс для анализа совместимости вакансий и резюме.

#### `__init__(config, ollama_model, ollama_url, timeout)`

Инициализация матчера.

**Параметры:**
- `config` (Config, optional): Объект конфигурации
- `ollama_model` (str, optional): Название модели Ollama (переопределяет config)
- `ollama_url` (str, optional): URL Ollama API (переопределяет config)
- `timeout` (int, optional): Таймаут в секундах (переопределяет config)

**Пример:**
```python
# С конфигом
config = Config("custom_config.json")
matcher = SmartJobMatcher(config=config)

# Без конфига (настройки по умолчанию)
matcher = SmartJobMatcher()

# С переопределением
matcher = SmartJobMatcher(
    ollama_model="llama3:8b",
    timeout=90
)
```

#### `match(job_description, resume_text, generate_feedback=True)`

Основной метод анализа совместимости.

**Параметры:**
- `job_description` (str): Текст описания вакансии
- `resume_text` (str): Текст резюме кандидата
- `generate_feedback` (bool, default=True): Генерировать ли текстовый фидбэк

**Возвращает:**
Dictionary с полями:
- `score` (int): Итоговый скор 0-100
- `report` (dict): Детальный отчёт
  - `score_details` (dict): Баллы по каждому критерию
  - `strengths` (list): Сильные стороны
  - `partial_match` (list): Частичные совпадения
  - `missing_required` (list): Отсутствующие требования
- `feedback` (str): Текстовый фидбэк (если generate_feedback=True)
- `debug` (dict, optional): Отладочная информация

**Пример:**
```python
result = matcher.match(
    job_description="Python разработчик...",
    resume_text="Опыт 3 года Python...",
    generate_feedback=True
)

print(f"Скор: {result['score']}/100")
print(f"Образование: {result['report']['score_details']['education']}")
print(f"Опыт: {result['report']['score_details']['experience']}")
print(f"Hard skills: {result['report']['score_details']['hard_skills']}")
print(f"Soft skills: {result['report']['score_details']['soft_skills']}")
```

#### `save_result(result, filepath=None)`

Сохранение результата анализа в JSON файл.

**Параметры:**
- `result` (dict): Результат от `match()`
- `filepath` (str, optional): Путь для сохранения (если None, генерируется автоматически)

**Возвращает:**
- `str`: Путь к сохранённому файлу

**Пример:**
```python
result = matcher.match(job, resume)

# Автоматическое имя файла
path = matcher.save_result(result)
# Сохранит в results/match_result_20250107_153000.json

# Явное указание пути
path = matcher.save_result(result, "my_analysis.json")
```

### Config

Класс для управления конфигурацией.

#### `__init__(config_path=None)`

**Параметры:**
- `config_path` (str, optional): Путь к JSON файлу конфигурации

**Пример:**
```python
# Загрузка из файла
config = Config("config.json")

# Настройки по умолчанию
config = Config()
```

#### `get(path, default=None)`

Получение значения конфигурации по пути.

**Параметры:**
- `path` (str): Путь через точку (например "ollama.model")
- `default` (Any): Значение по умолчанию

**Пример:**
```python
model = config.get("ollama.model")
# "llama3.2:3b"

timeout = config.get("ollama.timeout", 60)
# 60
```

#### `set(path, value)`

Установка значения конфигурации.

**Пример:**
```python
config.set("ollama.model", "llama3:8b")
config.set("scoring.weights.hard_skills_match", 50)
```

#### `save(output_path=None)`

Сохранение конфигурации в файл.

**Пример:**
```python
config.set("ollama.model", "llama3:8b")
config.save("my_config.json")
```

#### Свойства

```python
config.ollama_model     # Название модели
config.ollama_url       # URL API
config.ollama_timeout   # Таймаут
config.weights          # Веса для скоринга
```

## Формат конфигурации

```json
{
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
    "save_results": true,
    "results_dir": "results",
    "include_debug": true
  }
}
```

## Алгоритм скоринга

### 1. Парсинг (LLM)

LLM извлекает из текста:
- `education`: Описание образования
- `experience_years`: Опыт в годах (число)
- `hard_skills`: Список технических навыков
- `soft_skills`: Список личностных качеств

### 2. Расчёт скора (детерминированный)

**Образование** (макс. 25 баллов):
- Есть релевантное образование = 25
- Нет образования = 0

**Опыт** (макс. 25 баллов):
- Опыт >= требуемого = 25
- Опыт < требуемого = пропорционально (например, 2 года из 3 = 16.67)
- Нет опыта = 0

**Hard Skills** (макс. 40 баллов):
- Распределяется поровну на каждый требуемый навык
- Например, 5 навыков = 8 баллов за каждый
- Совпали 3 из 5 = 24 балла

**Soft Skills** (макс. 10 баллов):
- Аналогично hard skills
- Например, 2 качества = 5 баллов за каждое

### 3. Генерация фидбэка (LLM)

На основе структурированного отчёта LLM генерирует человекочитаемый текст с рекомендацией.

## Примеры использования

### Пример 1: Базовый анализ

```python
from matcher import SmartJobMatcher

matcher = SmartJobMatcher()

job = """
Backend Python разработчик.
Требования: опыт 3+ года, Django, PostgreSQL, Docker.
Высшее техническое образование.
"""

resume = """
Python разработчик, 4 года опыта.
Технологии: Django, PostgreSQL, Docker, Redis.
Образование: МФТИ, прикладная математика.
"""

result = matcher.match(job, resume)
print(f"Совместимость: {result['score']}/100")
```

### Пример 2: Пакетная обработка

```python
from matcher import SmartJobMatcher

matcher = SmartJobMatcher()

jobs = ["вакансия 1", "вакансия 2", "вакансия 3"]
resumes = ["резюме 1", "резюме 2", "резюме 3"]

results = []
for job in jobs:
    for resume in resumes:
        result = matcher.match(
            job,
            resume,
            generate_feedback=False  # Отключаем для скорости
        )
        results.append({
            'job': job,
            'resume': resume,
            'score': result['score']
        })

# Сортировка по убыванию скора
results.sort(key=lambda x: x['score'], reverse=True)

# ТОП-5 совпадений
for r in results[:5]:
    print(f"{r['score']}/100 - {r['job'][:30]}... ⟷ {r['resume'][:30]}...")
```

### Пример 3: Кастомизация весов

```python
from matcher import SmartJobMatcher

# Для стажёра: акцент на образование
matcher = SmartJobMatcher()
matcher.weights = {
    'education_match': 40,
    'experience_match': 10,
    'hard_skills_match': 35,
    'soft_skills_match': 15
}

result = matcher.match(intern_job, student_resume)
```

### Пример 4: Продвинутая конфигурация

```python
from matcher import SmartJobMatcher, Config

# Создание кастомной конфигурации
config = Config()
config.set("ollama.model", "llama3:8b")  # Более мощная модель
config.set("ollama.timeout", 120)         # Больше таймаут
config.set("scoring.weights.hard_skills_match", 50)  # Больше вес навыков
config.save("production_config.json")

# Использование
matcher = SmartJobMatcher(config=config)
result = matcher.match(job, resume)
```

## Устранение проблем

### Ollama недоступен

```
✗ Ollama сервер недоступен
```

**Решение:**
```bash
ollama serve
```

### Медленная работа

**Решение 1:** Используйте более лёгкую модель
```python
matcher = SmartJobMatcher(ollama_model="llama3.2:1b")
```

**Решение 2:** Увеличьте таймаут
```python
matcher = SmartJobMatcher(timeout=120)
```

**Решение 3:** Отключите генерацию фидбэка для пакетной обработки
```python
result = matcher.match(job, resume, generate_feedback=False)
```

### Ошибки парсинга JSON

LLM иногда возвращает невалидный JSON. Модуль автоматически обрабатывает такие ситуации, возвращая пустые данные и логируя ошибку.

Проверьте логи:
```bash
tail -f job_matcher.log
```

## Лучшие практики

### 1. Переиспользуйте экземпляр

```python
# ХОРОШО
matcher = SmartJobMatcher()
for job, resume in pairs:
    result = matcher.match(job, resume)

# ПЛОХО (создаёт новый экземпляр каждый раз)
for job, resume in pairs:
    matcher = SmartJobMatcher()
    result = matcher.match(job, resume)
```

### 2. Отключайте фидбэк для массовых операций

```python
# Для одной пары - включайте
result = matcher.match(job, resume, generate_feedback=True)

# Для сотен пар - отключайте
for job, resume in many_pairs:
    result = matcher.match(job, resume, generate_feedback=False)
```

### 3. Сохраняйте результаты

```python
result = matcher.match(job, resume)
matcher.save_result(result)  # Автоматически в results/
```

### 4. Используйте конфигурацию для разных сценариев

```python
# config_intern.json - для стажёров
config_intern = Config("config_intern.json")
matcher_intern = SmartJobMatcher(config=config_intern)

# config_senior.json - для сеньоров
config_senior = Config("config_senior.json")
matcher_senior = SmartJobMatcher(config=config_senior)
```

## Лицензия

MIT License

## Контакты

Для вопросов и предложений создавайте Issues в репозитории.
