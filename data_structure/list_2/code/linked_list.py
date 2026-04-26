class Node_(object):                        # Node class
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


class LinkedList_(object):                  # Linked List
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

    def __find_node_by_index(self, i):
        curr = self.__head
        for index in range(i + 1):
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
        if i < 0 or i > self.__size - 1:
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


if __name__ == "__main__":
    llist_ = LinkedList_()
    for n in range(5, 0, -1):
        llist_.append(n)
    print(llist_)
    llist_.pop(0)
    print(llist_)
    llist_.insert(2, 3)
    print(llist_)
    print(f"count(3): {llist_.count(3)}")
    print(f"get(2): {llist_.get(2)}")
