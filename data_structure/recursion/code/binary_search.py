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


if __name__ == "__main__":
    data = [2, 3, 5, 7, 9, 9, 10, 10, 12, 15, 19]
    print(f"data = {data}")

    print(f"binary_search_recusion(data, 5, 0, len(data))  = "
          f"{binary_search_recusion(data, 5, 0, len(data))}")
    print(f"binary_search_recusion(data, 13, 0, len(data)) = "
          f"{binary_search_recusion(data, 13, 0, len(data))}")

    print(f"binary_search_iter(data, 12) = {binary_search_iter(data, 12)}")
    print(f"binary_search_iter(data, 13) = {binary_search_iter(data, 13)}")
