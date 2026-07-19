# 순환(Recursion)

## 목차

- [핵심 요약](#핵심-요약)
- [1. 순환 알고리즘의 개념](#1-순환-알고리즘의-개념)
- [2. 순환의 예](#2-순환의-예)
- [3. 순환 알고리즘의 성능 분석](#3-순환-알고리즘의-성능-분석)
- [4. 다양한 알고리즘](#4-다양한-알고리즘)
- [실습 코드](#실습-코드)

---

## 핵심 요약

- **순환(recursion)** 은 함수가 자기 자신을 호출하여 문제를 해결하는 기법.
  문제의 정의 자체가 순환적일 때 자연스럽다.
- 순환 알고리즘은 반드시 **순환 호출을 멈추는 부분**(종료 조건)과
  **순환 호출을 하는 부분**을 가진다.
- 대부분의 순환은 **반복(iteration)으로 바꿀 수 있다**. 반복은 빠르지만,
  순환적인 문제에서는 프로그램 작성이 어려울 수 있다.
- 중복 계산이 많은 순환(예: 피보나치)은 **메모이제이션**으로 큰 성능 개선이 가능하다.

---

## 1. 순환 알고리즘의 개념

### 1.1 순환(Recursion)이란

- 알고리즘이나 함수가 수행 도중에 자기 자신을 다시 호출하여 문제를 해결하는 기법
- 문제의 정의 자체가 순환적으로 되어 있는 경우에 적합한 방법

컴퓨터에서의 repetition은 두 가지로 구현된다:

- **순환(recursion)**: 함수 호출 이용
- **반복(iteration)**: `for`나 `while`을 이용

대부분의 순환은 반복으로 바꾸어 작성할 수 있다.

**순환의 특징**

- 순환적인 문제에서는 자연스러운 방법이다.
- 함수 호출의 오버헤드가 발생한다.

**반복의 특징**

- 수행 속도가 빠르다.
- 순환적인 문제에 대해서는 프로그램 작성이 아주 어려울 수도 있다.

### 1.2 순환(Recursion) vs. 반복(Iteration)


| Item                | Recursion                            | Iteration                                     |
| --------------------- | -------------------------------------- | ----------------------------------------------- |
| Basic               | Function Call                        | Loop                                          |
| Format              | Termination Condition, Function Call | Initialization, Control Condition, Statements |
| Infinite Repetition | System Crash                         | Infinite Loop                                 |
| Stack               | Yes                                  | No                                            |
| Overhead            | Stack Frame                          | No                                            |
| Speed               | Slow                                 | Fast                                          |
| Code Size           | Reduced                              | Make longer                                   |

---

## 2. 순환의 예

이 장에서는 세 가지 예를 다룬다:

- **팩토리얼** — 순환에 적합한 예
- **피보나치 수열** — 순환이 비효율적인 예 (중복 계산)
- **이진검색** — 순환에 적합한 예 (분할정복)

### 2.1 팩토리얼

**수학적 정의**

```
n! = 1              if n = 0
n! = n * (n-1)!     if n >= 1
```

**순환 구현** ([`code/factorial.py`](./code/factorial.py))

```python
def factorial_recursive(n):
    if n > 1:
        return n * factorial_recursive(n - 1)
    return 1
```

**순환 알고리즘의 구조**

순환 알고리즘은 다음 두 부분을 반드시 포함한다:

- 순환 호출을 멈추는 부분 (종료 조건) — `if (n <= 1) return 1`
- 순환 호출을 하는 부분 — `else return n * factorial(n-1)`

순환 호출을 멈추는 부분이 없으면 시스템 오류가 발생할 때까지 무한정 호출된다.

**팩토리얼 함수의 호출 순서**

```
factorial(4) = 4 * factorial(3)
             = 4 * 3 * factorial(2)
             = 4 * 3 * 2 * factorial(1)
             = 4 * 3 * 2 * 1
             = 24
```

**반복 구현 — Python** ([`code/factorial.py`](./code/factorial.py))


| 순환 구조         | 반복 구조                          |
| ------------------- | ------------------------------------ |
| `n! = n * (n-1)!` | `n! = n * (n-1) * (n-2) * ... * 1` |

```python
def factorial_iter(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
```

### 2.2 피보나치 수열

**수학적 정의**

```
fib(n) = 0                        if n = 0
fib(n) = 1                        if n = 1
fib(n) = fib(n-2) + fib(n-1)      otherwise
```

수열: 0, 1, 1, 2, 3, 5, 8, 13, 21, ...

**순환에 적합하지 않은 문제**

피보나치를 순환으로 구현하면 **같은 항이 중복해서 계산**된다. 예를 들어
`fib(6)`을 호출하면 `fib(3)`이 3번이나 중복되어 계산되며, 이 현상은
`n`이 커질수록 더 심해진다.

```
            fib(6)
           /      \
       fib(4)    fib(5)
       /   \     /    \
   fib(2) fib(3) fib(3) fib(4)    ← fib(3)이 두 번 등장
   ...    ...    ...    ...
```

**순환 구현 — Python** ([`code/fibonacci.py`](./code/fibonacci.py))

```python
def fibonacci_recursive(n):
    return n if n < 2 else fibonacci_recursive(n-1) + fibonacci_recursive(n-2)
```

**반복 구현 — Python** ([`code/fibonacci.py`](./code/fibonacci.py))

```python
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
```

### 2.3 이진 검색

**순환에 적합한 문제.** 검색(Search) 문제에서 `n`개의 데이터가 크기 순으로
정렬되어 있다면 이진 검색(Binary Search)이 효율적이다.

**정의**

- `n`개의 데이터에 대한 이진검색 `binary-search(0, n-1)` 은 정렬된 데이터
  `n`개에서 전체 데이터의 중간에 있는 데이터(`n/2`)와 찾으려는 데이터(key)를
  비교하여 찾아가는 방법이다.
- 데이터가 정렬되어 있으므로 비교 후 찾으려는 데이터가 앞/뒤 리스트 중
  어느 부분에 있는지 알 수 있다.
- 운이 좋으면 정 가운데 데이터가 답이 되지만, 아닌 경우 앞 반절
  (`binary-search(0, n/2-1)`) 또는 뒤 반절 (`binary-search(n/2+1, n-1)`)에
  대해 다시 검색한다.
- 같은 방법으로 검색 대상 데이터가 1개일 때까지 진행한다.

**순환 구현 — Python** ([`code/binary_search.py`](./code/binary_search.py))

```python
def binary_search_recusion(arr, value, start, end):
    if start > end:
        return -1
    mid_idx = (start + end) // 2
    if value == arr[mid_idx]:
        return mid_idx
    elif value < arr[mid_idx]:
        return binary_search_recusion(arr, value, start, mid_idx - 1)
    else:
        return binary_search_recusion(arr, value, mid_idx + 1, end)
```

**반복 구현 — Python** ([`code/binary_search.py`](./code/binary_search.py))

```python
def binary_search_iter(arr, value):
    start_idx, end_idx = 0, len(arr)
    while start_idx < end_idx:
        mid_idx = (start_idx + end_idx) // 2
        if value == arr[mid_idx]:
            return mid_idx
        elif value < arr[mid_idx]:
            end_idx = mid_idx
        else:
            start_idx = mid_idx + 1
    return -1
```

---

## 3. 순환 알고리즘의 성능 분석

### 3.1 순환 알고리즘의 시간복잡도


| 문제     | 순환 알고리즘 | 반복 알고리즘 |
| ---------- | --------------- | --------------- |
| 팩토리얼 | O(n) + α     | O(n)          |
| 피보나치 | O(2ⁿ) + α   | O(n)          |
| 이진검색 | O(log n) + α | O(log n)      |

`α`는 함수 호출로 발생하는 오버헤드다. 피보나치의 경우 순환이 반복보다
**지수적으로 느리다**는 점에 주목.

### 3.2 이진검색 알고리즘의 성능 분석

이진검색은 매 단계에서 비교 연산 1번을 수행하고 문제 크기를 절반으로 줄인다.

```
T(n) = 1 + T(n/2)
T(1) = 1

T(2) = 1 + T(1)
T(4) = 1 + T(2) = 1 + 1 + T(1)
...
T(2ᵏ) = k + 1

n = 2ᵏ 이므로 k = log₂n
∴ T(n) = log₂n + 1 = O(log n)
```

### 3.3 함수의 수행시간 측정

Python에서 수행시간을 측정하는 방법들:

- **`math` 모듈의 내장 함수** — `math.factorial(n)`
- **`timeit.timeit()`** — 지정 횟수만큼 실행한 총 시간
- **`timeit.repeat()`** — 여러 번 반복해 리스트로 결과 반환
- **`%timeit`, `%%timeit`** — Jupyter Notebook의 매직 명령. 자동으로 적절한 반복 횟수 선택

```python
import timeit

timeit.timeit(stmt="math.factorial(x)", setup="x=10",
              number=1, globals={'math': math})
# → 3.2410000017080165e-06

timeit.repeat(stmt="math.factorial(x)", setup="x=10",
              number=1, globals={'math': math}, repeat=3)
# → [3.706e-06, 6.7e-07, 4.54e-07]
```

### 3.4 팩토리얼 수행시간 측정 결과

강의에서 `n=20` 으로 측정한 결과:


| 구현                      | 수행시간 (best of 10) |
| --------------------------- | ----------------------- |
| `factorial_recursive(20)` | 5.26 µs per loop     |
| `factorial_iter(20)`      | 3.33 µs per loop     |

반복 구현이 순환보다 약 1.6배 빠르다 (함수 호출 오버헤드 때문).

### 3.5 메모이제이션을 이용한 성능 개선

순환 호출에서 **같은 입력의 중복 계산**을 제거하기 위해 결과를 캐시에
저장하는 기법. 아래 `memo` 데코레이터를 함수에 붙이면 자동으로 캐시가 적용된다.
([`code/memoization.py`](./code/memoization.py))

```python
def memo(fn):
    cache = {}
    def wrapper(n):
        if n in cache:
            return cache[n]
        else:
            cache[n] = fn(n)
            return cache[n]
    return wrapper

@memo
def factorial_recursive2(n):
    return n * factorial_recursive2(n - 1) if n > 1 else 1
```

**팩토리얼 측정 결과**


| 구현                                    | 수행시간 (n=20, best of 10) |
| ----------------------------------------- | ----------------------------- |
| `factorial_recursive` (순환, 캐시 없음) | 5.26 µs                    |
| `factorial_iter` (반복)                 | 3.33 µs                    |
| `factorial_recursive2` (순환 + memo)    | 491 ns                      |

**피보나치 측정 결과**


| 구현                                    | 수행시간 (n=20, best of 10) |
| ----------------------------------------- | ----------------------------- |
| `fibonacci_recursive` (순환, 캐시 없음) | 2.79 ms                     |
| `fibonacci_recursive` + `@memo`         | 281 ns                      |

피보나치의 경우 메모이제이션 효과가 극적이다 — 중복 계산이 그만큼 많았다는 뜻.

**클래스 기반 구현** — 캐시를 객체 속성으로 관리하는 방식도 가능하다.

```python
class Fibonacci(object):
    def __init__(self):
        self.cache = {}

    def fib(self, n):
        if n < 2:
            return n
        elif n in self.cache:
            return self.cache[n]
        result = self.fib(n - 1) + self.fib(n - 2)
        self.cache[n] = result
        return result
```

### 3.6 이진검색 수행시간 측정 결과

강의에서 11개 원소 배열 `[2, 3, 5, 7, 9, 9, 10, 10, 12, 15, 19]`로 측정:


| 구현                            | 수행시간 (best of 10) |
| --------------------------------- | ----------------------- |
| `binary_search_recusion` (순환) | 713 ns                |
| `binary_search_iter` (반복)     | 761 ns                |
| `bisect.bisect` (Python 내장)   | 303 ns                |

Python 표준 라이브러리 `bisect` 모듈은 C로 구현되어 있어 가장 빠르다.

```python
from bisect import bisect
data = [2, 3, 5, 7, 9, 9, 10, 10, 12, 15, 19]
bisect(data, 3)   # → 2
bisect(data, 11)  # → 8
```

---

## 4. 다양한 알고리즘

### 4.1 분할정복 (Divide-and-Conquer) 알고리즘

- 순환: 팩토리얼, 이진검색
- 정렬: 합병 정렬, 퀵 정렬

### 4.2 그리디 (Greedy) 알고리즘

- 최소 비용 신장 트리
- 최단 경로 찾기

### 4.3 정렬 (Sorting) 알고리즘

- 버블 정렬, 선택 정렬, 삽입 정렬, 쉘 정렬
- 힙 정렬, 기수 정렬, 외부 정렬

---

## 실습 코드

- [`code/factorial.py`](./code/factorial.py) — 팩토리얼 (순환/반복)
- [`code/fibonacci.py`](./code/fibonacci.py) — 피보나치 수열 (순환/반복)
- [`code/binary_search.py`](./code/binary_search.py) — 이진 검색 (순환/반복)
- [`code/memoization.py`](./code/memoization.py) — `memo` 데코레이터와 `Fibonacci` 클래스
