class CircularQueue_(object):
    def __init__(self, n):
        self.__items = [None] * n
        self.__front = 0
        self.__rear = 0
        self.__size = n

    def __repr__(self):
        return repr(self.__items)

    @property
    def front(self):
        return None if self.is_empty() else self.__items[self.__front]

    @property
    def rear(self):
        return None if self.is_empty() else self.__items[self.__rear]

    def is_empty(self):
        return self.__items[self.__front] == None and self.__items[self.__rear] == None

    def is_full(self):
        return None not in self.__items

    def enqueue(self, data):
        if not self.__items[self.__rear]:
            self.__items[self.__rear] = data
            self.__rear = (self.__rear + 1) % self.__size

    def dequeue(self):
        if self.__items[self.__front]:
            data = self.__items[self.__front]
            self.__items[self.__front] = None
            self.__front = (self.__front + 1) % self.__size
            return data

    def clear(self):
        for i in range(self.__size):
            self.__items[i] = None
        self.__front = 0
        self.__rear = 0
        self.__size = 0


if __name__ == "__main__":
    cqueue_ = CircularQueue_(10)
    print(cqueue_)
    print(f"front: {cqueue_.front}")
    print(f"rear: {cqueue_.rear}")
    print(f"empty?: {cqueue_.is_empty()}", end="\n\n")

    for n in range(10, 0, -1):
        cqueue_.enqueue(n)
    print(cqueue_)
    print(f"front: {cqueue_.front}")
    print(f"rear: {cqueue_.rear}")
    print(f"full?: {cqueue_.is_full()}", end="\n\n")

    print(cqueue_.dequeue())
    print(cqueue_)
    print(f"front: {cqueue_.front}")
    print(f"rear: {cqueue_.rear}", end="\n\n")

    cqueue_.enqueue(2)
    print(cqueue_)
    print(f"front: {cqueue_.front}")
    print(f"rear: {cqueue_.rear}")
    print(f"full?: {cqueue_.is_full()}", end="\n\n")

    cqueue_.clear()
    print(cqueue_)
    print(f"front: {cqueue_.front}")
    print(f"rear: {cqueue_.rear}")
    print(f"empty?: {cqueue_.is_empty()}", end="\n\n")
