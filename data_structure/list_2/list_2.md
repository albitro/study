# 리스트(Lists) Ⅱ

## 목차

- [핵심 요약](#핵심-요약)
- [4. 리스트의 동적 구현](#4-리스트의-동적-구현)
  - [4.1 Linked List](#41-linked-list)
  - [4.2 Linked List의 장단점](#42-linked-list의-장단점)
  - [4.3 Linked List의 구조](#43-linked-list의-구조)
  - [4.4 Linked List의 종류](#44-linked-list의-종류)
  - [4.5 Singular Linked List (C)](#45-singular-linked-list-c)
  - [4.6 Circular Linked List (C)](#46-circular-linked-list-c)
  - [4.7 Double Linked List (C)](#47-double-linked-list-c)
  - [4.8 Singular Linked List (Python)](#48-singular-linked-list-python)
  - [4.9 Circular Linked List (Python)](#49-circular-linked-list-python)
  - [4.10 Double Linked List (Python)](#410-double-linked-list-python)
- [실습 코드](#실습-코드)

## 핵심 요약

- 리스트의 **동적 구현**은 노드를 메모리 곳곳에 분산 저장하고 링크 필드로 연결하는 방식이다.
- 단순 연결리스트는 한 방향 링크, 원형 연결리스트는 마지막 노드가 첫 노드를 가리키며, 이중 연결리스트는 양방향 링크를 갖는다.
- 단순 연결리스트의 핵심 연산은 삽입(3가지 경우), 삭제(2가지 경우), 방문, 탐색, 연결, 역순이다.
- 원형 연결리스트는 헤드포인터를 마지막 노드에 두면 처음·끝 삽입이 모두 용이하다.
- 이중 연결리스트는 헤드노드를 두어 삽입·삭제 코드를 간단하게 만든다.

## 4. 리스트의 동적 구현

### 4.1 Linked List

- 리스트의 항목들을 노드(node)라고 하는 곳에 분산하여 저장
- 다음 항목을 가리키는 주소도 같이 저장
- 노드(node) : `<항목, 주소>`
- 노드는 데이터 필드와 링크 필드로 구성
  - **데이터 필드** – 리스트의 원소, 즉 데이터 값을 저장하는 곳
  - **링크 필드** – 다른 노드의 주소값을 저장하는 장소 (포인터)
- 메모리 안에서의 노드의 물리적 순서가 리스트의 논리적 순서와 일치할 필요 없음

### 4.2 Linked List의 장단점


| 구분 | 내용                                                                           |
| ------ | -------------------------------------------------------------------------------- |
| 장점 | 삽입·삭제가 보다 용이하다 / 연속된 메모리 공간이 필요 없다 / 크기 제한이 없다 |
| 단점 | 구현이 어렵다 / 오류가 발생하기 쉽다                                           |

### 4.3 Linked List의 구조

- **노드 = 데이터 필드 + 링크 필드**
- **헤드 포인터(head pointer)**: 리스트의 첫 번째 노드를 가리키는 변수
- **노드의 생성**: 필요할 때마다 동적 메모리 생성을 이용하여 노드를 생성

### 4.4 Linked List의 종류


| 종류             | 특징                                           |
| ------------------ | ------------------------------------------------ |
| 단순 연결 리스트 | 마지막 노드의 링크가 NULL                      |
| 원형 연결 리스트 | 마지막 노드의 링크가 첫 번째 노드를 가리킴     |
| 이중 연결 리스트 | 각 노드가 선행 노드와 후속 노드 두 링크를 가짐 |

### 4.5 Singular Linked List (C)

#### 구조

- 하나의 링크 필드를 이용하여 연결
- 마지막 노드의 링크 값은 NULL

#### 노드 정의와 생성

```c
typedef int element;
typedef struct listnode {
    element data;
    struct listnode *link;
} ListNode;

ListNode *p1;
p1 = (ListNode *)malloc(sizeof(ListNode));
p1->data = 10;
p1->link = NULL;
```

두번째 노드 생성과 첫번째 노드와의 연결:

```c
ListNode *p2;
p2 = (ListNode *)malloc(sizeof(ListNode));
p2->data = 20;
p2->link = NULL;
p1->link = p2;
```

#### 삽입 연산

삽입 함수의 프로토타입:

```c
void insert_node(ListNode **phead, ListNode *p, ListNode *new_node)
```

- `phead`: 헤드 포인터 head에 대한 포인터
- `p`: 삽입될 위치의 선행 노드를 가리키는 포인터, 이 노드 다음에 삽입된다
- `new_node`: 새로운 노드를 가리키는 포인터

헤드포인터가 함수 안에서 변경되므로 헤드포인터의 포인터가 필요하다.

**삽입의 3가지 경우**


| 경우          | 처리                                                                                     |
| --------------- | ------------------------------------------------------------------------------------------ |
| `head`가 NULL | 공백 리스트에 삽입. 현재 삽입하려는 노드가 첫 번째 노드가 되므로 head의 값만 변경        |
| `p`가 NULL    | 새로운 노드를 리스트의 맨 앞에 삽입                                                      |
| 일반적인 경우 | `new_node`의 link에 `p->link` 값을 복사한 다음, `p->link`가 `new_node`를 가리키도록 한다 |

유사코드:

```
insert_node(L, before, new)

if L = NULL
then L←new
else new.link←before.link
     before.link←new
```

C 구현:

```c
// phead: 리스트의 헤드 포인터의 포인터
// p : 선행 노드
// new_node : 삽입될 노드
void insert_node(ListNode **phead, ListNode *p, ListNode *new_node)
{
    if( *phead == NULL ){          // 공백리스트인 경우
        new_node->link = NULL;
        *phead = new_node;
    }
    else if( p == NULL ){          // p가 NULL이면 첫번째 노드로 삽입
        new_node->link = *phead;
        *phead = new_node;
    }
    else {                         // p 다음에 삽입
        new_node->link = p->link;
        p->link = new_node;
    }
}
```

#### 삭제 연산

삭제 함수의 프로토타입:

```c
void remove_node(ListNode **phead, ListNode *p, ListNode *removed)
```

- `phead`: 헤드 포인터 head의 포인터
- `p`: 삭제될 노드의 선행 노드를 가리키는 포인터
- `removed`: 삭제될 노드를 가리키는 포인터

**삭제의 2가지 경우**


| 경우                   | 처리                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------- |
| `p`가 NULL             | 맨 앞의 노드를 삭제. 헤드포인터 변경                                                      |
| `p`가 NULL이 아닌 경우 | 중간 노드를 삭제.`removed` 앞의 노드인 `p`의 링크가 `removed` 다음 노드를 가리키도록 변경 |

유사코드:

```
remove_node(L, before, removed)

if L ≠ NULL
   then before.link←removed.link
        destroy(removed)
```

C 구현:

```c
// phead : 헤드 포인터에 대한 포인터
// p: 삭제될 노드의 선행 노드
// removed: 삭제될 노드
void remove_node(ListNode **phead, ListNode *p, ListNode *removed)
{
    if( p == NULL )
                *phead = (*phead)->link; // (*phead)가 가리키는 노드의 link
    else
                p->link = removed->link;
    free(removed);
}
```

#### 방문 (Traversal)

리스트 상의 노드를 순차적으로 방문한다. 반복과 순환 기법을 모두 사용 가능.

```c
void display(ListNode *head)
{
    ListNode *p=head;
    while( p != NULL ){
        printf("%d->", p->data);
        p = p->link;
    }
    printf("\n");
}
```

```c
void display_recur(ListNode *head)
{
    ListNode *p=head;
    if( p != NULL ){
        printf("%d->", p->data);
        display_recur(p->link);
    }
}
```

#### 탐색 (Search)

특정한 데이터 값을 갖는 노드를 찾는 연산.

```c
ListNode *search(ListNode *head, int x)
{
    ListNode *p;
    p = head;
    while( p != NULL ){
        if( p->data == x ) return p;   // 탐색 성공
        p = p->link;
    }
    return p;                          // 탐색 실패일 경우 NULL 반환
}
```

#### 연결 (Merge / Concat)

두 리스트를 연결한다.

```c
ListNode *concat(ListNode *head1, ListNode *head2)
{
    ListNode *p;
    if( head1 == NULL ) return head2;
    else if( head2 == NULL ) return head1;
    else {
        p = head1;
        while( p->link != NULL )
            p = p->link;
        p->link = head2;
        return head1;
    }
}
```

#### 역순 (Reverse)

리스트의 노드들을 역순으로 만드는 연산. 순회 포인터로 `p`, `q`, `r`을 사용한다.

```c
ListNode *reverse(ListNode *head)
{
    // 순회 포인터로 p, q, r을 사용
    ListNode *p, *q, *r;
    p = head;       // p는 역순으로 만들 리스트
    q = NULL;       // q는 역순으로 만들 노드
    while (p != NULL){
        r = q;      // r은 역순으로 된 리스트.   r은 q, q는 p를 차례로 따라간다.
        q = p;
        p = p->link;
        q->link =r; // q의 링크 방향을 바꾼다.
    }
    return q;       // q는 역순으로 된 리스트의 헤드 포인터
}
```

### 4.6 Circular Linked List (C)

#### 구조

- 마지막 노드의 링크가 첫 번째 노드를 가리키는 리스트
- 한 노드에서 다른 모든 노드로의 접근이 가능
- 보통 헤드포인터가 마지막 노드를 가리키게끔 구성하면 리스트의 처음이나 마지막에 노드를 삽입하는 연산이 단순 연결 리스트에 비하여 용이

#### 리스트의 처음에 삽입

```c
// phead: 리스트의 헤드 포인터의 포인터
// p : 선행 노드
// node : 삽입될 노드
void insert_first(ListNode **phead, ListNode *node)
{
    if( *phead == NULL ){
        *phead = node;
        node->link = node;
    }
    else {
        node->link = (*phead)->link;
        (*phead)->link = node;
    }
}
```

#### 리스트의 끝에 삽입

```c
// phead: 리스트의 헤드 포인터의 포인터
// p : 선행 노드
// node : 삽입될 노드
void insert_last(ListNode **phead, ListNode *node)
{
    if( *phead == NULL ){
        *phead = node;
        node->link = node;
    }
    else {
        node->link = (*phead)->link;
        (*phead)->link = node;
        *phead = node;
    }
}
```

### 4.7 Double Linked List (C)

#### 구조

- **단순 연결 리스트의 문제점**: 선행 노드를 찾기가 힘들다. 삽입이나 삭제 시에는 반드시 선행 노드가 필요하다.
- **이중 연결 리스트**: 하나의 노드가 선행 노드와 후속 노드에 대한 두 개의 링크를 가지는 리스트
- 링크가 양방향이므로 양방향으로 검색이 가능
- 단점은 공간을 많이 차지하고 코드가 복잡
- **실제 사용되는 형태**: 헤드노드 + 이중연결 리스트 + 원형연결 리스트

#### 헤드노드

- **헤드노드(head node)**: 데이터를 가지지 않고 단지 삽입, 삭제 코드를 간단하게 할 목적으로 만들어진 노드
- 헤드 포인터와의 구별 필요
- 공백상태에서는 헤드 노드만 존재

#### 노드 구조

```
| llink | data | rlink |
```

```c
typedef int element;
typedef struct DlistNode {
    element data;
    struct DlistNode *llink;
    struct DlistNode *rlink;
} DlistNode;
```

#### 삽입 연산

```c
// 노드 new_node를 노드 before의 오른쪽에 삽입한다.
void dinsert_node(DlistNode *before, DlistNode *new_node)
{
    new_node->llink = before;
    new_node->rlink = before->rlink;
    before->rlink->llink = new_node;
    before->rlink = new_node;
}
```

#### 삭제 연산

```c
// 노드 removed를 삭제한다.
void dremove_node(DlistNode *phead_node, DlistNode *removed)
{
    if( removed == phead_node ) return;
    removed->llink->rlink = removed->rlink;
    removed->rlink->llink = removed->llink;
    free(removed);
}
```

### 4.8 Singular Linked List (Python)

#### Node 클래스

```python
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
```

#### LinkedList 클래스

```python
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
```

#### 실행 예

```python
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
```

기대 출력:

```
5 4 3 2 1
4 3 2 1
4 3 3 2 1
count(3): 2
get(2): 3
```

### 4.9 Circular Linked List (Python)

```python
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
                prev = curr;
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
            if curr == self.__tail:
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
```

#### 실행 예

```python
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
```

기대 출력:

```
5 4 3 2 1
4 3 2 1
4 3 3 2 1
count(3): 2
get(2): 3
```

### 4.10 Double Linked List (Python)

#### DNode 클래스

```python
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
```

#### DoubleLinkedList 클래스

```python
class DoubleLinkedList_(object):
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

    # head, size 프로퍼티 (생략 — linked_list.py 패턴과 동일)

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
        for index in range(i+1):
            curr = curr.next
        return curr

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
        if i < 0 or i > self.__size-1:
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

    # is_empty, get, index, clear, count는 LinkedList_와 동일한 구조
```

#### 실행 예

```python
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
```

기대 출력:

```
5 4 3 2 1
4 3 2 1
4 3 3 2 1
count(3): 2
get(2): 3
```

## 실습 코드


| 파일                                                           | 설명                                                                  |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------- |
| [`code/linked_list.py`](code/linked_list.py)                   | 파이썬으로 구현한 단순 연결리스트 (Node + LinkedList) + 테스트        |
| [`code/circular_linked_list.py`](code/circular_linked_list.py) | 파이썬으로 구현한 원형 연결리스트 + 테스트                            |
| [`code/doubly_linked_list.py`](code/doubly_linked_list.py)     | 파이썬으로 구현한 이중 연결리스트 (DNode + DoubleLinkedList) + 테스트 |
