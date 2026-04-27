class Node_(object):
    def __init__(self, data=None, next=None):
        self.__data = data
        self.__next = next

    def __repr__(self):
        return str(self.__data)

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, arg):
        self.__data = arg

    @property
    def next(self):
        return self.__next

    @next.setter
    def next(self, arg):
        self.__next = arg


class LinkedList_(object):
    def __init__(self):
        self.__head = Node_()
        self.__size = 0

    def __repr__(self):
        list_ = []
        curr = self.__head.next
        while curr:
            list_.append(str(curr.data))
            curr = curr.next
        return " ".join(list_)

    @property
    def head(self):
        return self.__head

    @head.setter
    def head(self, arg):
        self.__head = arg

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, arg):
        self.__size = arg

    def __find_node_by_index(self, i):
        curr = self.__head
        for index in range(i+1):
            curr = curr.next
        return curr

    def is_empty(self):
        return self.__size == 0

    def get(self, i):
        if self.is_empty():
            return None
        if i < 0 or i > self.__size - 1:
            raise ValueError(f"out of bounds: index {i}")
        else:
            return self.__find_node_by_index(i).data

    def index(self, data):
        curr = self.__head.next
        for index in range(self.__size):
            if curr.data == data:
                return index
            else:
                curr = curr.next
        raise ValueError(f"not found: {data}")

    def append(self, data):
        prev = self.__find_node_by_index(self.__size - 1)
        new_node = Node_(data, prev.next)
        prev.next = new_node
        self.__size += 1

    def insert(self, i, data):
        if i < 0 or i > self.__size:
            raise ValueError(f"out of bounds: index {i}")
        else:
            prev = self.__find_node_by_index(i - 1)
            new_node = Node_(data, prev.next)
            prev.next = new_node
            self.__size += 1

    def pop(self, i):
        if i < 0 or i > self.__size-1:
            raise ValueError(f"out of bounds: index {i}")
        else:
            prev = self.__find_node_by_index(i - 1)
            curr = prev.next
            prev.next = curr.next
            self.__size -= 1
            return curr.data

    def remove(self, data):
        (prev, curr) = self.__find_node_by_data(data)
        if not curr:
            raise ValueError(f"not found: {data}")
        else:
            prev.next = curr.next
            self.__size -= 1
            return data

    def clear(self):
        self.__head = Node_()
        self.__size = 0

    def count(self, data):
        cnt = 0
        curr = self.__head.next
        while curr:
            if curr.data == data:
                cnt += 1
            curr = curr.next
        return cnt

    def __find_node_by_data(self, data):
        prev = self.__head
        curr = prev.next
        while curr:
            if curr.data == data:
                return (prev, curr)
            else:
                prev = curr
                curr = curr.next
        return (None, None)


class CircularLinkedList_(LinkedList_):
    def __init__(self):
        super().__init__()
        self.__tail = Node_()
        self.__tail.next = self.__tail
        self.head = self.__tail.next

    def __repr__(self):
        list_ = []
        curr = self.__tail.next.next
        while curr != self.head:
            list_.append(str(curr.data))
            curr = curr.next
        return " ".join(list_)

    @property
    def tail(self):
        return self.__tail

    @tail.setter
    def tail(self, arg):
        self.__tail = arg

    def __find_node_by_data(self, data):
        prev = self.__tail.next
        curr = prev.next
        while curr != self.head:
            if curr.data == data:
                return (prev, curr)
            else:
                prev = curr
                curr = curr.next
        return (None, None)

    def __find_node_by_index(self, i):
        curr = self.__tail.next
        for index in range(i+1):
            curr = curr.next
        return curr

    def is_empty(self):
        return self.size == 0

    def get(self, i):
        if self.is_empty():
            return None
        if i < 0 or i > self.size - 1:
            raise ValueError(f"out of bounds: index {i}")
        else:
            return self.__find_node_by_index(i).data

    def index(self, data):
        curr = self.__tail.next
        for index in range(self.size):
            if curr.data == data:
                return index
            else:
                curr = curr.next
        raise ValueError(f"not found: {data}")

    def append(self, data):
        new_node = Node_(data, self.__tail.next)
        self.__tail.next = new_node
        self.__tail = new_node
        self.size += 1

    def insert(self, i, data):
        if i < 0 or i > self.size:
            raise ValueError(f"out of bounds: index {i}")
        else:
            prev = self.__find_node_by_index(i - 1)
            new_node = Node_(data, prev.next)
            prev.next = new_node
            if i == self.size:
                self.__tail = new_node
            self.size += 1

    def pop(self, i):
        if i < 0 or i > self.size-1:
            raise ValueError(f"out of bounds: index {i}")
        else:
            prev = self.__find_node_by_index(i - 1)
            curr = prev.next
            prev.next = curr.next
            if i == self.size - 1:
                self.__tail = prev
            self.size -= 1
            return curr.data

    def remove(self, data):
        (prev, curr) = self.__find_node_by_data(data)
        if not curr:
            raise ValueError(f"not found: {data}")
        else:
            prev.next = curr.next
            if curr == self.__tail:
                self.__tail = prev
            self.size -= 1
            return data

    def clear(self):
        self.__tail = Node_()
        self.__tail.next = self.__tail
        self.size = 0

    def count(self, data):
        cnt = 0
        curr = self.__tail.next.next
        while curr != self.head:
            if curr.data == data:
                cnt += 1
            curr = curr.next
        return cnt


if __name__ == "__main__":
    # 강의 p.32 — LinkedQueue_를 사용한 사용 예이지만,
    # 강의 슬라이드의 별도 LinkedQueue_ 정의 페이지가 본 자료에는
    # 명시적으로 제시되지 않았다. 따라서 실행 예는 LinkedList_ 기반으로 대체한다.
    llqueue_ = LinkedList_()
    print(f"front: {llqueue_.head.next}")
    # try:
    #     print(llqueue_.dequeue())
    # except IndexError as ie:
    #     print(ie.args)

    for n in range(5, 0, -1):
        llqueue_.append(n)
    print(llqueue_)
    print(f"size: {llqueue_.size}", end="\n\n")

    print(llqueue_.pop(0))
    print(llqueue_)
    print(f"size: {llqueue_.size}", end="\n\n")

    llqueue_.append(2)
    llqueue_.append(3)
    print(llqueue_)
    print(f"size: {llqueue_.size}")