def selection_sort(list, n):
    for i in range(0, n - 1):
        least = i
        for j in range(i + 1, n):          # 최소값 탐색
            if list[j] < list[least]:
                least = j
        list[i], list[least] = list[least], list[i]  # SWAP


if __name__ == "__main__":
    data = [5, 3, 8, 1, 2, 7]
    selection_sort(data, len(data))
    print(data)
