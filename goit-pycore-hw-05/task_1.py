from typing import Callable, Dict


def caching_fibonacci() -> Callable[[int], int]:
    """Return a fibonacci(n) function that caches already computed values."""
    # The cache lives in the enclosing scope, so the inner function
    # keeps access to it between calls (this is a closure).
    cache: Dict[int, int] = {}

    def fibonacci(n: int) -> int:
        # Base cases of the sequence
        if n <= 0:
            return 0
        if n == 1:
            return 1
        # Return a value that was computed before
        if n in cache:
            return cache[n]

        # Compute recursively, store in the cache and return
        cache[n] = fibonacci(n - 1) + fibonacci(n - 2)
        return cache[n]

    return fibonacci


if __name__ == "__main__":
    # Get the fibonacci function
    fib = caching_fibonacci()

    # Use it to compute Fibonacci numbers
    print(fib(10))  # 55
    print(fib(15))  # 610
