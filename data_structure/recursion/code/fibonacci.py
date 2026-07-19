def fibonacci_recursive(n):
    return n if n < 2 else fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


def fib_iter(n):
    if n < 2:
        return n

    last = 0
    current = 1
    for i in range(2, n + 1):
        tmp = current
        current += last
        last = tmp
    return current


if __name__ == "__main__":
    for n in range(10):
        print(f"fib({n}): recursive={fibonacci_recursive(n)}, iter={fib_iter(n)}")
