# goit-pycore-hw-05

Домашнє завдання до Теми 8 курсу «Python Programming: Foundations and Best Practices 2.0»: елементи функціонального програмування.

| Файл | Завдання |
| --- | --- |
| `task_1.py` | `caching_fibonacci()`: замикання з кешем, рекурсивне обчислення чисел Фібоначчі |
| `task_2.py` | `generator_numbers(text)`: генератор дійсних чисел у тексті; `sum_profit(text, func)` рахує загальний дохід |
| `task_3.py` | Аналіз лог-файлу: статистика за рівнями та записи вибраного рівня (необов'язкове завдання) |
| `task_4.py` | Консольний бот-помічник з обробкою помилок через декоратор `input_error` |

Зовнішніх залежностей немає, потрібна тільки стандартна бібліотека Python 3.9+.

## Запуск

```bash
python task_1.py
python task_2.py
python task_3.py data/logfile.log
python task_3.py data/logfile.log error
python task_4.py
```

`data/logfile.log` — приклад лог-файлу з умови завдання.
