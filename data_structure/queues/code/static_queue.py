class ListQueue_(object):
    def __init__(self):
        self.__items = []

    def __repr__(self):
        return repr(self.__items)

    @property
    def front(self):
        return None if self.is_empty() else self.__items[0]

    @property
    def tail(self):
        return None if self.is_empty() else self.__items[-1]

    @property
    def size(self):
        return len(self.__items)

    def is_empty(self):
        return len(self.__items) == 0

    def enqueue(self, *data):
        self.__items.extend(data)

    def dequeue(self):
        return self.__items.pop(0)

    def clear(self):
        self.__items.clear()


if __name__ == "__main__":
    lqueue_ = ListQueue_()
    print(f"front: {lqueue_.front}")
    print(f"tail: {lqueue_.tail}")
    try:
        print(lqueue_.dequeue())
    except IndexError as ie:
        print(ie.args)

    for n in range(5, 0, -1):
        lqueue_.enqueue(n)
    print(lqueue_)
    print(f"front: {lqueue_.front}")
    print(f"tail: {lqueue_.tail}")
    print(f"size: {lqueue_.size}", end="\n\n")

    print(lqueue_.dequeue())
    print(lqueue_)
    print(f"front: {lqueue_.front}")
    print(f"tail: {lqueue_.tail}")
    print(f"size: {lqueue_.size}", end="\n\n")

    lqueue_.enqueue(2, 3)
    print(lqueue_)
    print(f"front: {lqueue_.front}")
    print(f"tail: {lqueue_.tail}")
    print(f"size: {lqueue_.size}")
