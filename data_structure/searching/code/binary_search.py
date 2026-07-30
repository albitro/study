def binary_search(lst, n, key):
    left = 0
    right = n - 1
    while left <= right:
        mid = (left + right) // 2
        if lst[mid] == key:
            return mid
        elif lst[mid] < key:
            left = mid + 1
        else:
            right = mid - 1
    return -1


if __name__ == "__main__":
    data = [9, 15, 16, 19, 21, 39, 51, 65, 76, 85, 99]
    target = 65
    result = binary_search(data, len(data), target)
    print(f"검색 배열: {data}")
    print(f"찾는 값: {target}")
    print(f"반환된 인덱스: {result}")
