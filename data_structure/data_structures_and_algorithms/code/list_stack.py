class ListStack_(object):
    def __init__(self):
        self.__items = []

    def __repr__(self):
        return repr(self.__items)

    @property
    def top(self):
        return None if self.is_empty() else self.__items[-1]

    @property
    def size(self):
        return len(self.__items)

    def is_empty(self):
        return len(self.__items) == 0

    def push(self, *data):
        self.__items.extend(data)

    def pop(self):
        return self.__items.pop()

    def clear(self):
        self.__items.clear()


if __name__ == "__main__":
    lstack_ = ListStack_()
    print(lstack_.top)  # None

    try:
        print(lstack_.pop())
    except IndexError as ie:
        print(ie.args)   # ('pop from empty list',)

    for n in range(5, 0, -1):
        lstack_.push(n)
    print(lstack_)                               # [5, 4, 3, 2, 1]
    print(f"top: {lstack_.top}")                 # top: 1
    print(f"size: {lstack_.size}", end="\n\n")   # size: 5

    print(lstack_.pop())                         # 1
    print(lstack_)                               # [5, 4, 3, 2]
    print(f"top: {lstack_.top}")                 # top: 2
    print(f"size: {lstack_.size}", end="\n\n")   # size: 4

    lstack_.push(2, 3, 4)
    print(lstack_)                               # [5, 4, 3, 2, 2, 3, 4]
    print(f"top: {lstack_.top}")                 # top: 4
    print(f"size: {lstack_.size}")               # size: 7
