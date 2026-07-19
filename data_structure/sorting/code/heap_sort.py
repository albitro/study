import sys

MAX_ELEMENTS = 200
heap = [0] * MAX_ELEMENTS      # heap[1..n] 사용
n = 0


def HEAP_FULL(n):
    return n == MAX_ELEMENTS - 1


def HEAP_EMPTY(n):
    return not n


def insert_max_heap(item):
    global n
    if HEAP_FULL(n):
        sys.stderr.write("The heap is full. \n")
        sys.exit(1)
    n += 1
    i = n
    while (i != 1) and (item > heap[i // 2]):     # /*1*/
        heap[i] = heap[i // 2]
        i //= 2
    heap[i] = item


def delete_max_heap():
    global n
    if HEAP_EMPTY(n):
        sys.stderr.write("The heap is empty\n")
        sys.exit(1)
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
    return item


def adjust(list, root, n):
    temp = list[root]
    rootkey = list[root]
    child = 2 * root                              # left child
    while child <= n:
        if (child < n) and (list[child] < list[child + 1]):
            child += 1
        if rootkey > list[child]:
            break
        else:
            list[child // 2] = list[child]
            child *= 2
    list[child // 2] = temp


def heapsort(list, n):
    for i in range(n // 2, 0, -1):                # /*1*/
        adjust(list, i, n)
    for i in range(n - 1, 0, -1):                 # /*2*/
        list[1], list[i + 1] = list[i + 1], list[1]   # SWAP(list[1], list[i+1])
        adjust(list, 1, i)


if __name__ == "__main__":
    # 배열 첨자 1부터 저장: index 0은 자리만 채운다.
    data = [0, 26, 5, 77, 1, 61, 11, 59, 15, 48, 19]
    heapsort(data, len(data) - 1)
    print(data[1:])
