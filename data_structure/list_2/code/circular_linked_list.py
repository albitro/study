from linked_list import Node_, LinkedList_


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
        for index in range(i + 1):
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
        if i < 0 or i > self.size - 1:
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
    cllist_ = CircularLinkedList_()
    for n in range(5, 0, -1):
        cllist_.append(n)
    print(cllist_)
    cllist_.pop(0)
    print(cllist_)
    cllist_.insert(2, 3)
    print(cllist_)
    print(f"count(3): {cllist_.count(3)}")
    print(f"get(2): {cllist_.get(2)}")
