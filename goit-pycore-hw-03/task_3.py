import re


def normalize_phone(phone_number: str) -> str:
    """Normalize a phone number to the '+380XXXXXXXXX' format.

    All characters except digits and a leading '+' are removed. If the
    international code is missing, '+38' (Ukraine) is added; a number that
    already starts with '380' only gets the '+'.
    """
    phone = re.sub(r"[^\d+]", "", phone_number.strip())
    # keep '+' only at the very beginning
    phone = phone[0] + phone[1:].replace("+", "") if phone else phone

    if phone.startswith("+"):
        return phone
    if phone.startswith("380"):
        return "+" + phone
    return "+38" + phone


if __name__ == "__main__":
    raw_numbers = [
        "067\t123 4567",
        "(095) 234-5678\n",
        "+380 44 123 4567",
        "380501234567",
        "    +38(050)123-32-34",
        "     0503451234",
        "(050)8889900",
        "38050-111-22-22",
        "38050 111 22 11   ",
    ]

    sanitized_numbers = [normalize_phone(num) for num in raw_numbers]
    print("Нормалізовані номери телефонів для SMS-розсилки:", sanitized_numbers)
