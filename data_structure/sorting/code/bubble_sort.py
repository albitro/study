def bubble_sort(list, n):
    for i in range(n - 1, 0, -1):          # /*1*/
        for j in range(0, i):              # /*2*/
            if list[j] > list[j + 1]:      # /*3*/
                list[j], list[j + 1] = list[j + 1], list[j]  # SWAP


def bubble_sort_improved(list, n):
    flag = 1
    i = n - 1
    while flag > 0:                        # /*1*/
        flag = 0
        for j in range(0, i):              # /*2*/
            if list[j] > list[j + 1]:
                list[j], list[j + 1] = list[j + 1], list[j]  # SWAP
                flag = 1                   # /*3*/
        i -= 1


if __name__ == "__main__":
    data1 = [15, 4, 8, 3, 50, 9, 20]
    bubble_sort(data1, len(data1))
    print(data1)

    data2 = [15, 4, 8, 3, 50, 9, 20]
    bubble_sort_improved(data2, len(data2))
    print(data2)
