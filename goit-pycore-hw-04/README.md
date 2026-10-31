# goit-pycore-hw-04

Домашнє завдання до Теми 6 курсу «Python Programming: Foundations and Best Practices 2.0»: робота з файлами та модульна система.

| Файл | Завдання |
| --- | --- |
| `task_1.py` | `total_salary(path)` — загальна та середня зарплата з файлу `data/salary_file.txt` |
| `task_2.py` | `get_cats_info(path)` — список словників з інформацією про котів з `data/cats_file.txt` |
| `task_3.py` | Кольорове дерево директорії (colorama), шлях передається аргументом командного рядка |
| `task_4.py` | Консольний бот-помічник: `hello`, `add`, `change`, `phone`, `all`, `close`/`exit` |

## Віртуальне оточення

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск

```bash
python task_1.py
python task_2.py
python task_3.py picture
python task_4.py
```

Папка `picture` — тестова директорія для `task_3.py` зі структурою з умови завдання.
