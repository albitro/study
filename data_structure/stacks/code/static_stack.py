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
    print(lstack_.top)
    try:
        print(lstack_.pop())
    except IndexError as ie:
        print(ie.args)

    for n in range(5, 0, -1):
        lstack_.push(n)
    print(lstack_)
    print(f"top: {lstack_.top}")
    print(f"size: {lstack_.size}", end="\n\n")

    print(lstack_.pop())
    print(lstack_)
    print(f"top: {lstack_.top}")
    print(f"size: {lstack_.size}", end="\n\n")

    lstack_.push(2, 3, 4)
    print(lstack_)
    print(f"top: {lstack_.top}")
    print(f"size: {lstack_.size}")
