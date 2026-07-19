def quicksort(list, left, right):
    if left < right:                              # 분할
        i = left
        j = right + 1
        pivot = list[left]
        while True:
            while True:
                i += 1
                if not (i <= right and list[i] < pivot):
                    break
            while True:
                j -= 1
                if not (list[j] > pivot):
                    break
            if i < j:
                list[i], list[j] = list[j], list[i]   # SWAP
            else:
                break
        list[left], list[j] = list[j], list[left]     # SWAP
        quicksort(list, left, j - 1)
        quicksort(list, j + 1, right)


if __name__ == "__main__":
    data = [26, 5, 37, 1, 61, 11, 59, 15, 48, 19]
    quicksort(data, 0, len(data) - 1)
    print(data)
