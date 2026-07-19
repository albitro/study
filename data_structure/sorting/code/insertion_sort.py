def insertion_sort(list, n):
    for i in range(1, n):
        next = list[i]
        j = i - 1
        while j >= 0 and next < list[j]:
            list[j + 1] = list[j]
            j -= 1
        list[j + 1] = next


if __name__ == "__main__":
    data1 = [5, 4, 3, 2, 1]
    insertion_sort(data1, len(data1))
    print(data1)

    data2 = [3, 2, 5, 1, 4]
    insertion_sort(data2, len(data2))
    print(data2)
