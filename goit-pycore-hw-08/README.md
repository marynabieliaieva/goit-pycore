# goit-pycore-hw-08

Домашнє завдання до Теми 12 курсу «Python Programming: Foundations and Best Practices 2.0»: серіалізація та десеріалізація адресної книги за допомогою `pickle`.

Бот-помічник з [goit-pycore-hw-07](https://github.com/marynabieliaieva/goit-pycore/tree/goit-pycore-hw-07/goit-pycore-hw-07) тепер не втрачає дані: при виході адресна книга зберігається у файл, а при наступному запуску відновлюється з нього.

| Файл | Що містить |
| --- | --- |
| `address_book.py` | Класи `Field`, `Name`, `Phone` (10 цифр), `Birthday` (DD.MM.YYYY), `Record`, `AddressBook` |
| `storage.py` | `save_data(book, filename)` і `load_data(filename)` на `pickle` |
| `main.py` | Бот: `main()` завантажує книгу при старті й зберігає її при виході |

## Як працює збереження

- `load_data()` читає `addressbook.pkl` поруч із `main.py`. Якщо файлу ще немає, повертає нову порожню `AddressBook`; якщо файл пошкоджений або містить не адресну книгу, перейменовує його на `addressbook.pkl.bak` (щоб наступне збереження його не затерло), попереджає й починає з порожньої книги.
- `save_data()` викликається в блоці `finally`, тож дані зберігаються при `close` / `exit`, при Ctrl+C, при кінці вводу (Ctrl+D / Ctrl+Z) і навіть після неочікуваної помилки.
- Запис іде спочатку в тимчасовий файл, який потім атомарно замінює `addressbook.pkl`, тож перерваний запис не зіпсує попередні дані.
- `addressbook.pkl` (і його `.tmp` / `.bak`) додано до `.gitignore`.

## Команди

| Команда | Що робить |
| --- | --- |
| `add [ім'я] [телефон]` | Додати новий контакт або телефон до наявного |
| `change [ім'я] [старий телефон] [новий телефон]` | Змінити телефон контакту |
| `phone [ім'я]` | Показати телефони контакту |
| `all` | Показати всі контакти |
| `add-birthday [ім'я] [DD.MM.YYYY]` | Додати дату народження |
| `show-birthday [ім'я]` | Показати дату народження |
| `birthdays` | Дні народження на наступні 7 днів (вихідні переносяться на понеділок) |
| `hello` | Привітання |
| `close` / `exit` | Зберегти дані й вийти |

Зовнішніх залежностей немає, потрібна тільки стандартна бібліотека Python 3.9+.

## Запуск

```bash
python main.py
```

## Приклад: дані між сеансами

```text
$ python main.py
Welcome to the assistant bot!
Enter a command: add John 1234567890
Contact added.
Enter a command: add-birthday John 15.05.1990
Birthday added.
Enter a command: exit
Good bye!

$ python main.py
Welcome to the assistant bot!
Enter a command: all
Contact name: John, phones: 1234567890, birthday: 15.05.1990
```
