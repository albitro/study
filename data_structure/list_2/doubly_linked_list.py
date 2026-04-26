from linked_list import Node_


class DNode_(Node_):                        # Node of Double Linked List class
    def __init__(self, data=None, next=None, prev=None):
        super().__init__(data, next)
        self.__prev = prev

    @property
    def prev(self):
        return self.__prev

    @prev.setter
    def prev(self, arg):
        self.__prev = arg


class DoubleLinkedList_(object):            # Double Linked List
    def __init__(self):
        self.__head = DNode_()
        self.__head.next = self.__head
        self.__head.prev = self.__head
        self.__size = 0

    def __repr__(self):
        list_ = []
        curr = self.__head.next
        while curr != self.__head:
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
        curr = self.__head.next
        while curr != self.__head:
            if curr.data == data:
                return curr
            else:
                curr = curr.next
        return None

    def __find_node_by_index(self, i):
        curr = self.__head            # index: -1
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
        prev = self.__head.prev
        new_node = DNode_(data, self.__head, prev)
        prev.next = new_node
        self.__head.prev = new_node
        self.__size += 1

    def insert(self, i, data):
        if i < 0 or i > self.__size:
            raise ValueError(f"out of bounds: index {i}")
        else:
            prev = self.__find_node_by_index(i - 1)
            new_node = DNode_(data, prev.next, prev)
            new_node.next.prev = new_node
            prev.next = new_node
            self.__size += 1

    def pop(self, i):
        if i < 0 or i > self.__size - 1:
            raise ValueError(f"out of bounds: index {i}")
        else:
            curr = self.__find_node_by_index(i)
            curr.prev.next = curr.next
            curr.next.prev = curr.prev
            self.__size -= 1
            return curr.data

    def remove(self, data):
        curr = self.__find_node_by_data(data)
        if not curr:
            raise ValueError(f"not found: {data}")
        else:
            curr.prev.next = curr.next
            curr.next.prev = curr.prev
            self.__size -= 1
            return data

    def clear(self):
        self.__head = DNode_()
        self.__head.next = self.__head
        self.__head.prev = self.__head
        self.__size = 0

    def count(self, data):
        cnt = 0
        curr = self.__head.next
        while curr != self.__head:
            if curr.data == data:
                cnt += 1
            curr = curr.next
        return cnt


if __name__ == "__main__":
    dllist_ = DoubleLinkedList_()
    for n in range(5, 0, -1):
        dllist_.append(n)
    print(dllist_)
    dllist_.pop(0)
    print(dllist_)
    dllist_.insert(2, 3)
    print(dllist_)
    print(f"count(3): {dllist_.count(3)}")
    print(f"get(2): {dllist_.get(2)}")
