# 7. 큐(Queues)

## 목차

- [핵심 요약](#핵심-요약)
- [1. 큐 추상데이터타입](#1-큐-추상데이터타입)
- [2. 큐의 정적 구현](#2-큐의-정적-구현)
- [3. 원형 큐](#3-원형-큐)
- [4. 큐의 동적 구현](#4-큐의-동적-구현)
- [5. 데크](#5-데크)
- [6. 우선순위 큐](#6-우선순위-큐)
- [Summary](#summary)
- [실습 코드](#실습-코드)

## 핵심 요약

- **큐**는 한쪽 끝(rear)에서 삽입, 반대쪽 끝(front)에서 삭제가 일어나는 **FIFO(First In First Out)** 자료구조.
- **선형 큐**는 자료가 쌓이면 앞이 비어도 뒤로 더 못 넣어 자료 이동이 필요해진다. 이 문제를 해결하려고 **원형 큐**를 사용한다 (`(rear+1) % MAX_QUEUE_SIZE`).
- 원형 큐는 초기값 `front = rear = 0`이고, 최대 `MAX_QUEUE_SIZE - 1`개를 저장한다.
- **연결 큐**는 연결리스트로 구현하며 `front`/`rear` 포인터를 사용한다.
- **데크(Deque)** 는 양쪽 끝에서 모두 삽입·삭제가 가능한 큐.
- **우선순위 큐**는 FIFO가 아니라 우선순위가 높은 데이터가 먼저 나간다.

---

## 1. 큐 추상데이터타입

### 1.1 큐 ADT

- 객체: n개의 element형으로 구성된 요소들의 순서있는 모임
- 연산:


| 연산            | 설명                                            |
| ----------------- | ------------------------------------------------- |
| `create()`      | 큐를 생성한다.                                  |
| `init(q)`       | 큐를 초기화한다.                                |
| `is_empty(q)`   | 큐가 비어있는지를 검사한다.                     |
| `is_full(q)`    | 큐가 가득 찼는가를 검사한다.                    |
| `enqueue(q, e)` | 큐의 뒤에 요소를 추가한다.                      |
| `dequeue(q)`    | 큐의 앞에 있는 요소를 반환한 다음 삭제한다.     |
| `peek(q)`       | 큐에서 삭제하지 않고 앞에 있는 요소를 반환한다. |

### 1.2 큐

- 순서 있는 리스트
- 삽입 연산은 한쪽 끝에서 일어난다. (rear라고 부른다)
- 삭제 연산은 삽입의 반대쪽에서 일어난다. (front라고 부른다)
- **FIFO (First In First Out)**

```
                   A          insert(A)
                   ↑
                  rear
                   A B        insert(B)
                 ↑   ↑
              front rear
                   A B C      insert(C)
                 ↑     ↑
              front   rear
                     B C      delete(A)
                   ↑   ↑
                front rear
                     B C D    insert(D)
                   ↑     ↑
                front   rear
```

---

## 2. 큐의 정적 구현

### 2.1 큐의 생성

1차원 배열의 사용, `front`와 `rear` 변수 사용.

```c
/* 1차원 배열의 사용, front와 rear 변수 사용 */
#define MAX_QUEUE_SIZE 100
typedef struct {
        int key;
        /* other fields */
} element;

element queue[MAX_QUEUE_SIZE];
int rear = -1;
int front = -1;
```

### 2.2 큐의 삽입 (Enqueue)

```c
void enqueue(int *rear, element item) {
    if (*rear == MAX_QUEUE_SIZE - 1) {
        queue_full();
        /* 처리방법 - 큐의 원소를 모두 원쪽으로 이동 */
        return;
    }
    queue[++*rear] = item;
}
```

### 2.3 큐의 삭제 (Dequeue)

```c
element dequeue(int *front, int rear)
{
    if (*front == rear)
        return queue_empty();
            /* return an error key */
    return queue[++*front];
}
```

### 2.4 큐의 검사 (isempty / isfull)

```c
/* 큐가 비어있는지 검사하는 함수 */
int isempty()
{ if ( front == rear ) return(1);
  else return(0); }

/* 큐가 가득 차 있는지 검사하는 함수 */
int isfull()
{ if ( rear == MAX_QUEUE_SIZE - 1 )
        return(1);
  else return(0); }
```

### 2.5 큐의 구현 — C

```c
#include <stdio.h>
#define MAX 5
int queue[MAX];
int front = -1, rear = -1;

int isempty() {
    if (rear == front) {
        printf("\n Queue Underflow!");
        return (1);
    }
    else return (0);
}

int isfull() {
    if (rear == MAX-1) {
        printf("\n Queue Overflow!");
        return (1);
    }
    else return (0);
}

void enqueue(int item) {
    if (isfull()) return;
    queue[++rear] = item;
    printf("\n Enqueue(%d)", queue[rear]);
}

void dequeue() {
    if (isempty()) return;
    printf("\n Dequeue():%d", queue[++front]);
}

int peek() {
    int i = 0;
    if (isempty()) return(-1);
    if (front == -1) return queue[i];
    return queue[front];
}

void display() {
    int i;
    if (isempty()) return;
    else {
        printf("\nThe element in Queue :\n");
        if (front == -1) {
            for (i=front+1 ; i <= rear ; i++)
                printf("  %d", queue[i]);
        }
        else {
            for (i=front ; i <= rear ; i++)
                printf("  %d", queue[i]);
        }
    }
}

int main () {
    int n, val=0;
    for (n = 5; n >= 1 ; n--) {
        enqueue(n);
    }
    display();
    val =  peek();
    if (val == -1) {
        printf("\n There is no element in queue!");
    }
    else
        printf("\n Peek():%d",val);
    for (n = 5 ; n >= 1 ; n--) {
        dequeue();
    }
    enqueue(2);

    return 0;
}
```

기대 출력:

```
 Enqueue(5)
 Enqueue(4)
 Enqueue(3)
 Enqueue(2)
 Enqueue(1)
The element in Queue :
  5  4  3  2  1
 Peek():5
 Dequeue():5
 Dequeue():4
 Dequeue():3
 Dequeue():2
 Dequeue():1
 Queue Overflow!
```

### 2.6 큐의 구현 — Python

`code/static_queue.py` 참고.

---

## 3. 원형 큐

### 3.1 큐의 연산 (선형 큐의 동작)

```
[공백 큐 생성]              [원소 A 삽입]              [원소 B 삽입]
                              [0]                       [0] [1]
   ┌──┬──┬──┐              ┌──┬──┬──┐                ┌──┬──┬──┐
 Q │  │  │  │            Q │ A│  │  │              Q │ A│ B│  │
   └──┴──┴──┘              └──┴──┴──┘                └──┴──┴──┘
   ↑↑                       ↑   ↑                     ↑      ↑
 front=rear=-1           front=-1 rear=0           front=-1  rear=1

[원소 삭제]                [원소 C 삽입]              [원소 삭제]
   ┌──┬──┬──┐              ┌──┬──┬──┐                ┌──┬──┬──┐
 Q │ A│ B│  │            Q │  │ B│ C│              Q │  │  │ C│
   └──┴──┴──┘              └──┴──┴──┘                └──┴──┴──┘
       ↑   ↑                  ↑      ↑                       ↑↑
    front rear             front   rear                front=rear=2
```

### 3.2 원형 큐

**선형 큐(Linear Queue)의 구현에서 문제점**

- front와 rear의 값이 계속 증가만 하기 때문에 배열에 끝에 도달하고
- 삭제로 큐의 앞부분이 비어있더라도 사용하지 못한다.
- 자료의 이동이 필요하다.

**해결 방안**

- 배열을 원형으로 만들고 원형 배열에 데이터를 저장한다.
- 초기값 front와 rear는 0으로 만든다. (-1이 아님)
- front 변수는 큐의 처음 값 위치에서 1을 뺀 값이다.
- rear 변수는 큐의 마지막 값 위치를 가리킨다.
- 최대 `MAX_QUEUE_SIZE – 1` 개를 저장한다. (`MAX_QUEUE_SIZE` 가 아님!!)

### 3.3 원형 큐 예시


| 상태                                | front | rear | 비고          |
| ------------------------------------- | ------- | ------ | --------------- |
| 비어있는 큐                         | 0     | 0    | front == rear |
| J1, J2, J3 삽입                     | 0     | 3    |               |
| J1~J5 삽입 (Full)                   | 0     | 5    |               |
| J6, J7 삽입 (rear가 한 바퀴 돌아감) | 4     | 1    |               |
| J6~J9 삽입 (Full)                   | 4     | 3    |               |

### 3.4 원형 큐 연산

- enqueue 연산 후 rear의 값: `*rear = (*rear + 1) % MAX_QUEUE_SIZE;`
- dequeue 연산 후 front의 값: `*front = (*front + 1) % MAX_QUEUE_SIZE;`

### 3.5 원형 큐의 삽입

```c
void enqueue(int front, int *rear, element item) {
    *rear = (*rear + 1) % MAX_QUEUE_SIZE;
    if (front == *rear) {
        queue_full(rear);
            /* reset rear and print error */
        return;
    }
    queue[*rear] = item;
}
```

### 3.6 원형 큐의 삭제

```c
element dequeue(int *front, int rear) {
/* remove front element from the queue and put it in item */
    element item;
    if (*front == rear)
        return queue_empty();
            /*queue_empty returns an error key*/
    *front = (*front + 1) % MAX_QUEUE_SIZE;
    return queue[*front];
}
```

### 3.7 원형 큐의 구현 — C

```c
#include <stdio.h>
#define MAX 6
int queue[MAX];
int front = 0, rear = 0;

void cenqueue(int item) {
    if (front == ((rear+1) % MAX)) {
        printf("\n Queue is full!");
        return;
    }
    rear = (rear+1) % MAX;
    queue[rear] = item;
    printf("\n Enqueue(%d)", queue[rear]);
}

void cdequeue() {
    if (rear == front) {
        printf("\n Queue is emtpy!");
        return;
    }
    front = (front+1) % MAX;
    printf("\n Dequeue():%d", queue[front]);
}

void display() {
    int i;
    printf("\nThe element in Queue :\n");
    if (rear == front) {
        printf(" Queue empty!");
        return;
    }
    if (front > rear) i = 0;
    else if (front == 0) i = front + 1;
         else i = front;
    while ( i <= rear )
        printf(" %d", queue[i++]);
}

int main () {
    int n, val=0;
    for (n = 5; n >= 1 ; n--) {
        cenqueue(n);
    }
    display();
    for (n = 5 ; n >= 1 ; n--) {
        cdequeue();
    }
    cenqueue(2);
    cenqueue(3);
    display();

    return 0;
}
```

기대 출력:

```
 Enqueue(5)
 Enqueue(4)
 Enqueue(3)
 Enqueue(2)
 Enqueue(1)
The element in Queue :
 5 4 3 2 1
 Dequeue():5
 Dequeue():4
 Dequeue():3
 Dequeue():2
 Dequeue():1
 Enqueue(2)
 Enqueue(3)
The element in Queue :
 2 3
```

### 3.8 원형 큐의 구현 — Python

`code/circular_queue.py` 참고.

---

## 4. 큐의 동적 구현

### 4.1 연결된 리스트로 구현하는 큐

- **연결된 큐 (linked queue)**: 연결리스트로 구현된 큐
- `front` 포인터는 삭제와 관련되며 `rear` 포인터는 삽입과 관련된다.
- `front`는 연결 리스트의 맨 앞에 있는 요소를 가리키며, `rear` 포인터는 맨 뒤에 있는 요소를 가리킨다.
- 큐에 요소가 없는 경우에는 `front`와 `rear`는 `NULL`

```
front                                         rear
  ↓                                            ↓
┌────┐    ┌────┐    ┌────┐    ┌────┐
│A │ ●┼──→│B │ ●┼──→│C │ ●┼──→│D │ ●┼──→ NULL
└────┘    └────┘    └────┘    └────┘
```

### 4.2 삽입과 삭제

- **원소의 삽입**: 새 노드를 만들어 `rear`의 link로 연결하고, `rear`를 새 노드로 갱신한다.
- **원소의 삭제**: `temp = front`, `front = front->link`, `temp` 해제. front가 NULL이면 빈 큐이다.

### 4.3 큐의 구현 — C

```c
#include <stdio.h>
#include <stdlib.h>

typedef int element;

typedef struct node{
    element item;
    struct node *link;
} QueueNode;

typedef struct{
    QueueNode *front, *rear;
} LinkedQueueType;

QueueNode *temp=NULL, *p=NULL;
LinkedQueueType *lq=NULL, *ptr=NULL;

void lenqueue(LinkedQueueType *lq, element item) {
    temp = (QueueNode *)malloc(sizeof(QueueNode));
    if(temp == NULL){
        fprintf(stderr, "메모리 할당에러\n");
        return;
    }
    else{
        temp->item = item;
        if (lq->front == NULL) {
            lq->front = temp;
        }
        else {
            lq->rear->link = temp;
        }
        lq->rear = temp;
        printf("\nLinked Queue Enqueue(%d)", temp->item);
    }
}

element ldequeue(LinkedQueueType *lq){
    temp = lq->front;
    if(lq->front == NULL) {
        fprintf(stderr, "\nQueue is empty!\n");
        exit(1);
    }
    else{
        QueueNode *temp=lq->front;
        int item = temp->item;
        lq->front = lq->front->link;
        if (lq->front == NULL) lq->rear = NULL;
        free(temp);
        return item;
    }
}

int main () {
    int  i;
    LinkedQueueType *ptr=NULL;
    QueueNode *p=NULL;

    ptr = (LinkedQueueType *)malloc(sizeof(LinkedQueueType));
    ptr->front = NULL;
    ptr->rear = NULL;

    lenqueue(ptr, 5);
    lenqueue(ptr, 4);
    lenqueue(ptr, 3);
    lenqueue(ptr, 2);
    lenqueue(ptr, 1);

    p = ptr->front;
    printf("\n The elements in Queue \n");
    while(p) {
        printf(" %d", p->item);
        p = p->link;
    }

    while(ptr->front){
        i = ldequeue(ptr);
        printf("\nLinked Queue Dnqueue():%d", i);
    }

    i = ldequeue(ptr);

    return 0;
}
```

기대 출력:

```
Linked Queue Enqueue(5)
Linked Queue Enqueue(4)
Linked Queue Enqueue(3)
Linked Queue Enqueue(2)
Linked Queue Enqueue(1)
 The elements in Queue
 5 4 3 2 1
Linked Queue Dnqueue():5
Linked Queue Dnqueue():4
Linked Queue Dnqueue():3
Linked Queue Dnqueue():2
Linked Queue Dnqueue():1
Queue is empty!
```

### 4.4 큐의 구현 — Python

`code/linked_queue.py` 참고.

---

## 5. 데크

### 5.1 데크(Deque)

- **Double-ended queue**
- 큐의 전단(front)와 후단(rear)에서 모두 삽입과 삭제가 가능한 큐

```
   add_front ↘                       ↙ add_rear
              ┌─────────────────┐
delete_front ←│   ┌──┬──┬──┐    │→ delete_rear
              │   │  │  │  │    │
   get_front ←│   └──┴──┴──┘    │→ get_rear
              └─────────────────┘
              전단(front)    후단(rear)
```

### 5.2 데크의 연산


| 연산               | 동작          |
| -------------------- | --------------- |
| `add_front(dq, A)` | 전단에 A 삽입 |
| `add_rear(dq, B)`  | 후단에 B 삽입 |
| `add_front(dq, C)` | 전단에 C 삽입 |
| `add_rear(dq, D)`  | 후단에 D 삽입 |
| `delete_front(dq)` | 전단 삭제     |
| `delete_rear(dq)`  | 후단 삭제     |

### 5.3 데크의 동적 구현

양쪽에서 삽입, 삭제가 가능하여야 하므로 일반적으로 **이중 연결 리스트** 사용.

```c
typedef int element;          // 요소의 타입

typedef struct DlistNode {    // 노드의 타입
   element data;
   struct DlistNode *llink;
   struct DlistNode *rlink;
} DlistNode;

typedef struct DequeType {    // 덱의 타입
   DlistNode *head;
   DlistNode *tail;
} DequeType;
```

### 5.4 데크의 동적 구현 — 삽입 연산

연결리스트의 연산과 유사. 헤드포인터 대신 `head`와 `tail` 포인터 사용.

```c
void add_rear(DequeType *dq, element item)
{
  DlistNode *new_node =  create_node(dq->tail, item, NULL);
  if( is_empty(dq))
     dq->head = new_node;
  else
     dq->tail->rlink = new_node;
  dq->tail = new_node;
}

void add_front(DequeType *dq, element item)
{
  DlistNode *new_node = create_node(NULL, item, dq->head);

  if( is_empty(dq))
        dq->tail = new_node;
  else
        dq->head->llink = new_node;
  dq->head = new_node;
}
```

### 5.5 데크의 동적 구현 — 삭제 연산

연결리스트의 연산과 유사.

```c
element delete_front(DequeType *dq)
{
        element item;
        DlistNode *removed_node;

        if (is_empty(dq))   error("공백 덱에서 삭제");
        else {
                removed_node = dq->head;     // 삭제할 노드
                item = removed_node->data;  // 데이터 추출
                dq->head = dq->head->rlink; // 헤드 포인터 변경
                free(removed_node);          // 메모리 공간 반납
                if (dq->head == NULL)     // 공백상태이면
                        dq->tail = NULL;
                else      // 공백상태가 아니면
                        dq->head->llink=NULL;
        }
        return item;
}
```

---

## 6. 우선순위 큐

### 6.1 우선순위 큐(Priority Queue)

- 가장 일반적인 큐: 스택이나 큐를 우선순위 큐로 구현할 수 있다.
- **우선순위 큐 (priority queue)**: 우선순위를 가진 항목들을 저장하는 큐로 순서가 아니라 우선 순위가 높은 데이터가 먼저 나가게 된다.


| 자료구조   | 삭제되는 요소               |
| ------------ | ----------------------------- |
| 스택       | 가장 최근에 들어온 데이터   |
| 큐         | 가장 먼저 들어온 데이터     |
| 우선순위큐 | 가장 우선순위가 높은 데이터 |

**응용분야**

- 시뮬레이션 시스템 (여기서의 우선 순위는 대개 사건의 시각이다.)
- 네트워크 트래픽 제어
- 운영 체제에서의 작업 스케쥴링

### 6.2 우선순위 큐의 구현

- 배열을 이용한 우선순위 큐
- 연결리스트를 이용한 우선순위 큐
- 히프(heap)를 이용한 우선순위 큐

---

## Summary

- 큐 또한 리스트의 특별한 형태로 삽입과 삭제가 한쪽 끝에서만 일어난다. 삽입과 삭제는 서로 반대쪽에서 일어나는 것이 스택과 다르다. 문이 두개인 마을버스의 타는 곳과 내리는 곳이 따로 있어서 먼저 탄 사람이 먼저 내리는 구조이다. (First In First Out, FIFO)
- 큐를 구현할 때는 일반 배열을 사용하면 자료를 이동해야 하는 불편함이 있어서 일반 배열을 원형으로 만들어서 원형 배열을 이용하여 구현한다.
- Deque은 double-ended queue로 큐의 전단과 후단에서 모두 삽입과 삭제가 가능한 큐이다.
- 큐의 응용으로는 서로 다른 속도로 실행되는 두 프로세스간의 상호작용을 조화시키는 버퍼가 있다.
- 큐잉 이론에 따라 컴퓨터로 시스템의 특성을 시뮬레이션하여 분석하는데 이용된다. 큐잉 모델은 서비스를 수행하는 Server와 서비스를 제공받는 Client로 이루어지며, 제한된 수의 Server 때문에 Client들은 대기행렬에서 기다리게 되는데 이 대기행렬을 큐로 구현한다.
- 우선순위 큐는 우선순위를 가진 항목들을 저장하는 큐로 FIFO 순서가 아니라 우선 순위가 높은 데이터가 먼저 나가게 된다.

---

## 실습 코드


| 파일                                               | 설명                                                                  |
| ---------------------------------------------------- | ----------------------------------------------------------------------- |
| [`code/static_queue.py`](code/static_queue.py)     | 정적 큐의 Python 구현 (`ListQueue_` 클래스)                           |
| [`code/circular_queue.py`](code/circular_queue.py) | 원형 큐의 Python 구현 (`CircularQueue_` 클래스)                       |
| [`code/linked_queue.py`](code/linked_queue.py)     | 연결 큐의 Python 구현 (`Node_`, `LinkedList_`, `CircularLinkedList_`) |
