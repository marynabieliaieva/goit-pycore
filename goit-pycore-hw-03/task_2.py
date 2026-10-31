import random


def get_numbers_ticket(min: int, max: int, quantity: int) -> list[int]:
    """Return a sorted list of `quantity` unique random numbers in [min, max].

    Constraints: 1 <= min <= max <= 1000 and quantity must fit into the range.
    If any constraint is violated, an empty list is returned.
    """
    if not all(isinstance(value, int) for value in (min, max, quantity)):
        return []
    if min < 1 or max > 1000 or min > max:
        return []
    if quantity < 1 or quantity > max - min + 1:
        return []

    # random.sample picks without repetition, so all numbers are unique
    numbers = random.sample(range(min, max + 1), quantity)
    return sorted(numbers)


if __name__ == "__main__":
    lottery_numbers = get_numbers_ticket(1, 49, 6)
    print("Ваші лотерейні числа:", lottery_numbers)
    print(get_numbers_ticket(0, 49, 6))
    print(get_numbers_ticket(1, 10, 20))
