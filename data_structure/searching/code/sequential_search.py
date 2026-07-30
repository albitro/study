def sequential_search(keys, find_key, n):
    i = 0
    while i <= n:
        i += 1
        if keys[i] == find_key:
            return i
    return 0


if __name__ == "__main__":
    data = [10, 13, 25, 4, 15, 20, 5, 29, 14, 21]
    target = 15
    result = sequential_search(data, target, len(data))
    print(f"검색 배열: {data}")
    print(f"찾는 값: {target}")
    print(f"반환된 인덱스: {result}")