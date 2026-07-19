MAX_ELEMENTS = 200


def insert_max_heap(heap, n, item):
    if n == MAX_ELEMENTS - 1:
        raise OverflowError("The heap is full.")
    n += 1
    i = n
    while (i != 1) and (item > heap[i // 2]):
        heap[i] = heap[i // 2]
        i //= 2
    heap[i] = item
    return n


if __name__ == "__main__":
    heap = [0] * MAX_ELEMENTS  # heap[0]은 사용하지 않음
    n = 0
    for value in (20, 15, 2, 14, 10):
        n = insert_max_heap(heap, n, value)

    print("heap:", *heap[1:n + 1])
