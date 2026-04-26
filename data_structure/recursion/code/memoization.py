def memo(fn):
    cache = {}

    def wrapper(n):
        if n in cache:  # n이 cache에 있으면 fn(n) 호출에 대해 n의 캐시 값 cache[n]을 읽어서 반환합니다.
            return cache[n]
        else:
            cache[n] = fn(n)  # fn(n) 호출이 반환한 값을 캐시 값 cache[n]으로 저장하고 반환합니다.
            return cache[n]
    return wrapper


@memo
def factorial_recursive2(n):
    return n * factorial_recursive2(n - 1) if n > 1 else 1


class Fibonacci(object):

    def __init__(self):
        self.cache = {}

    def fib(self, n):
        if n < 2:
            return n
        elif n in self.cache:  # 딕셔너리 cache에 키 n이 있으면 값을 읽어와 바로 반환합니다.
            return self.cache[n]

        # cache에 키 n이 없으면 fib(n-1)과 fib(n-2)의 값을 더한 값을 cache에 저장하고 그 값을 반환합니다.
        result = self.fib(n - 1) + self.fib(n - 2)
        self.cache[n] = result

        return result

    def __repr__(self):  # 메소드 오버라이딩
        return repr(self.cache)


if __name__ == "__main__":
    print(f"factorial_recursive2(20) = {factorial_recursive2(20)}")

    fib_obj = Fibonacci()
    print(f"fib_obj.fib(20) = {fib_obj.fib(20)}")
    print(f"fib_obj.cache   = {fib_obj}")
