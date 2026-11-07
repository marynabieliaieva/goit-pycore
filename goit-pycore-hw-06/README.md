# goit-pycore-hw-06

Домашнє завдання до Теми 9 курсу «Python Programming: Foundations and Best Practices 2.0»: основи роботи з класами.

Файл `address_book.py` містить адресну книгу для майбутнього бота-помічника:

| Клас | Що робить |
| --- | --- |
| `Field` | Базовий клас для полів запису |
| `Name` | Ім'я контакту, обов'язкове поле |
| `Phone` | Номер телефону з валідацією: рівно 10 цифр |
| `Record` | Контакт: ім'я та список телефонів; `add_phone`, `remove_phone`, `edit_phone`, `find_phone` |
| `AddressBook` | Сховище записів на основі `UserDict`; `add_record`, `find`, `delete` |

Зовнішніх залежностей немає, потрібна тільки стандартна бібліотека Python 3.9+.

## Запуск

```bash
python address_book.py
```
