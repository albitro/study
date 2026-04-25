# 배열 A에서 최대값을 찾아 반환
def array_max(A):
    tmp = A[0]
    for i in range(1, len(A)):
        if tmp < A[i]:
            tmp = A[i]
    return tmp


def array_max_pythonic(A):
    tmp = A[0]
    for item in A:
        if item > tmp:
            tmp = item
    return tmp


if __name__ == "__main__":
    scores = [80, 70, 90, 30, 85, 60]

    print(f"입력 배열: {scores}")
    print(f"array_max:          {array_max(scores)}")
    print(f"array_max_pythonic: {array_max_pythonic(scores)}")
