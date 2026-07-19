MAX_ELEMENTS = 200


def insert_max_heap(heap, n, item):
    n += 1
    i = n
    while (i != 1) and (item > heap[i // 2]):
        heap[i] = heap[i // 2]
        i //= 2
    heap[i] = item
    return n


def delete_max_heap(heap, n):
    if n == 0:
        raise IndexError("The heap is empty")
    item = heap[1]
    temp = heap[n]
    n -= 1
    parent = 1
    child = 2
    while child <= n:
        if (child < n) and (heap[child] < heap[child + 1]):
            child += 1
        if temp >= heap[child]:
            break
        heap[parent] = heap[child]
        parent = child
        child *= 2
    heap[parent] = temp
    return item, n


if __name__ == "__main__":
    heap = [0] * MAX_ELEMENTS
    n = 0
    for value in (20, 15, 2, 14, 10):
        n = insert_max_heap(heap, n, value)

    removed, n = delete_max_heap(heap, n)
    print("deleted:", removed)
    print("heap after delete:", *heap[1:n + 1])
