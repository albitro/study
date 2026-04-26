def factorial_recursive(n):
    if n > 1:
        return n * factorial_recursive(n - 1)
    return 1


def factorial_iter(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


if __name__ == "__main__":
    n = 5
    print(f"factorial_recursive({n}) = {factorial_recursive(n)}")
    print(f"factorial_iter({n})      = {factorial_iter(n)}")

    n = 10
    print(f"factorial_recursive({n}) = {factorial_recursive(n)}")
    print(f"factorial_iter({n})      = {factorial_iter(n)}")
