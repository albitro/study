# 리스트(Lists) Ⅰ

## 목차

- [핵심 요약](#핵심-요약)
- [1. 구현을 위한 기초](#1-구현을-위한-기초)
  - [1.1 자료구조의 구현 방식](#11-자료구조의-구현-방식)
  - [1.2 배열(Array)](#12-배열array)
  - [1.3 배열의 추상데이터타입](#13-배열의-추상데이터타입)
  - [1.4 1차원 배열과 2차원 배열](#14-1차원-배열과-2차원-배열)
  - [1.5 구조체](#15-구조체)
  - [1.6 자기참조구조체](#16-자기참조구조체)
  - [1.7 포인터](#17-포인터)
  - [1.8 배열과 포인터](#18-배열과-포인터)
  - [1.9 동적 메모리 할당](#19-동적-메모리-할당)
  - [1.10 Python Built-in 자료구조](#110-python-built-in-자료구조)
  - [1.11 Class](#111-class)
- [2. 리스트 추상데이터타입](#2-리스트-추상데이터타입)
- [3. 리스트의 정적 구현](#3-리스트의-정적-구현)
  - [3.1 리스트의 구현 방식](#31-리스트의-구현-방식)
  - [3.2 배열로 구현된 리스트](#32-배열로-구현된-리스트)
  - [3.3 ArrayListType의 구현 (C)](#33-arraylisttype의-구현-c)
  - [3.4 파이썬 리스트](#34-파이썬-리스트)
  - [3.5 파이썬 ArrayList 클래스](#35-파이썬-arraylist-클래스)
- [실습 코드](#실습-코드)

## 핵심 요약

- 자료구조는 **정적 구현**(배열/리스트)과 **동적 구현**(연결리스트)으로 나뉜다.
- 배열의 ADT는 `<인덱스, 요소>` 쌍의 집합이며, `create`, `retrieve`, `store` 연산을 갖는다.
- 리스트의 정적 구현은 1차원 배열에 항목을 순서대로 저장하며, 삽입/삭제 시 데이터 이동이 필요하다.
- C에서는 `ArrayListType` 구조체로, 파이썬에서는 내장 list 또는 `ArrayList` 클래스로 구현한다.

## 1. 구현을 위한 기초

### 1.1 자료구조의 구현 방식


| 구현 방식              | 언어별 도구                                       |
| ------------------------ | --------------------------------------------------- |
| 정적 구현              | 배열(C), 리스트(Python)                           |
| 동적 구현 (연결리스트) | 자기참조구조체(C: 구조체, 포인터), 클래스(Python) |

### 1.2 배열(Array)

같은 형의 변수를 여러 개 만드는 경우에 사용한다.

```c
int A0, A1, A2, A3, ..., A9;
int A[10];
```

반복 코드 등에서 배열을 사용하면 효율적인 프로그래밍이 가능하다.

예) 최대값을 구하는 프로그램: 만약 배열이 없었다면 일일이 비교해야 한다.

```c
tmp = score[0];
for (i = 1; i < n; i++) {
    if (score[i] > tmp)
        tmp = score[i];
}
```

### 1.3 배열의 추상데이터타입

배열은 `<인덱스, 요소>` 쌍의 집합이며, 인덱스가 주어지면 해당되는 요소가 대응되는 구조이다.

```
배열 ADT
객체: <i, element> 쌍의 집합
연산:
  create(n)         ::= n개의 요소를 가진 배열의 생성
  retrieve(A, i)    ::= 배열 A의 i번째 요소 반환
  store(A, i, item) ::= 배열 A의 i번째 위치에 item 저장
```

### 1.4 1차원 배열과 2차원 배열

`int A[6];`은 base 주소부터 `sizeof(int)` 단위로 6개의 칸이 연속 배치된다. `A[i]`의 주소는 `base + i * sizeof(int)`이다.

`int A[3][4];`는 논리적으로는 3행 4열이지만, 실제 메모리 안에서는 `A[0][0], A[0][1], ..., A[0][3], A[1][0], ..., A[2][3]` 순서로 1차원으로 배치된다.

### 1.5 구조체

- **구조체(structure)**: 타입이 다른 데이터를 하나로 묶는 방법
- **배열(array)**: 타입이 같은 데이터들을 하나로 묶는 방법

```c
struct example {
    char cfield;
    int ifield;
    float ffield;
    double dfield;
};
struct example s1;
```

`typedef`을 이용한 구조체 선언:

```c
typedef struct person {
    char name[10];     // 문자배열로 된 이름
    int age;           // 나이를 나타내는 정수값
    float height;      // 키를 나타내는 실수값
} person;
person a;              // 구조체 변수 선언
```

**구조체의 대입과 비교 연산**

- 구조체 변수의 대입: 가능 (`a = b;`)
- 구조체 변수끼리 비교: 불가능 (`if (a > b)`는 컴파일 오류)

### 1.6 자기참조구조체

자기참조구조체(self-referential structure)는 구조체의 필드 중에 자기 자신을 가리키는 포인터가 한 개 이상 존재하는 구조체이다. 연결리스트나 트리에 많이 등장한다.

```c
typedef struct ListNode {
    char data[10];
    struct ListNode *link;
} ListNode;
```

### 1.7 포인터

포인터는 다른 변수의 주소를 가지고 있는 변수이다.

```c
char a = 'A';
char *p;
p = &a;
*p = 'B';      // 포인터가 가리키는 내용을 B로 변경
```

**관련 연산자**

- `&` 연산자: 변수의 주소를 추출
- `*` 연산자: 포인터가 가리키는 곳의 내용을 추출


| 표현     | 의미                                                    |
| ---------- | --------------------------------------------------------- |
| `p`      | 포인터                                                  |
| `*p`     | 포인터가 가리키는 값                                    |
| `*p++`   | 포인터가 가리키는 값을 가져온 다음, 포인터를 한 칸 증가 |
| `*p--`   | 포인터가 가리키는 값을 가져온 다음, 포인터를 한 칸 감소 |
| `(*p)++` | 포인터가 가리키는 값을 증가시킴                         |

**포인터의 종류**

```c
void *p;          // p는 아무것도 가리키지 않는 포인터
int *pi;          // pi는 정수 변수를 가리키는 포인터
float *pf;        // pf는 실수 변수를 가리키는 포인터
char *pc;         // pc는 문자 변수를 가리키는 포인터
int **pp;         // pp는 포인터를 가리키는 포인터
struct test *ps;  // ps는 test 타입의 구조체를 가리키는 포인터
void (*f)(int a); // f는 함수를 가리키는 포인터
```

**포인터의 형변환**

```c
void *p;
pi = (int *) p;
```

**포인터 연산** — 포인터에 대한 사칙연산은 포인터가 가리키는 객체 단위로 계산된다.


| 표현  | 의미                                    |
| ------- | ----------------------------------------- |
| `p`   | 포인터                                  |
| `p+1` | 포인터 p가 가리키는 객체의 바로 뒤 객체 |
| `p-1` | 포인터 p가 가리키는 객체의 바로 앞 객체 |

**포인터의 포인터** — `int **pp`처럼 포인터를 가리키는 포인터도 가능하다.

**포인터 사용시 유의할 점**

- 포인터가 아무것도 가리키고 있지 않을 때는 `NULL`로 설정 (`int *pi = NULL;`)
- 초기화가 안 된 상태에서 사용 금지
- 포인터 타입간의 변환시에는 명시적인 타입 변환 사용

### 1.8 배열과 포인터

- 배열의 이름은 사실상의 포인터와 같은 역할을 한다.
- 컴파일러가 배열의 이름을 배열의 첫번째 주소로 대치한다.

**구조체의 포인터** — 구조체의 요소에 접근하는 연산자는 `->`이다.

```c
struct { int i; float f; } s, *ps;
ps = &s;
ps->i = 2;
ps->f = 3.14;
```

### 1.9 동적 메모리 할당

**정적 메모리 할당**

- 메모리의 크기는 프로그램이 시작하기 전에 결정
- 프로그램의 수행 도중에 그 크기가 변경될 수 없음
- 처음에 결정된 크기보다 큰 입력 → 처리 불가, 작은 입력 → 메모리 낭비
- 예) 변수나 배열의 선언

**동적 메모리 할당**

- 프로그램의 실행 도중에 메모리를 할당받는 것
- 필요한 만큼만 할당받아 사용하고 반납
- 메모리를 매우 효율적으로 사용 가능

**전형적인 동적 메모리 할당 코드**

```c
main()
{
    int *pi;
    pi = (int *)malloc(sizeof(int));   // 동적 메모리 할당
    ...                                 // 동적 메모리 사용
    free(pi);                           // 동적 메모리 반납
}
```

**관련 라이브러리 함수**


| 함수           | 설명                                     |
| ---------------- | ------------------------------------------ |
| `malloc(size)` | size 바이트 만큼의 메모리 블록을 할당    |
| `free(ptr)`    | ptr이 가리키는 할당된 메모리 블록을 해제 |
| `sizeof(var)`  | 변수나 타입의 크기 반환 (바이트 단위)    |

```c
(char *)malloc(100);                          /* 100바이트로 100개의 문자를 저장 */
(int *)malloc(sizeof(int));                   /* 정수 1개를 저장할 메모리 확보 */
(struct Book *)malloc(sizeof(struct Book));   /* 하나의 구조체 생성 */
```

### 1.10 Python Built-in 자료구조


| 분류       | 타입  | 특징                                                                     |
| ------------ | ------- | -------------------------------------------------------------------------- |
| Sequence   | tuple | 반복 순회 가능, 중복 허용, 인덱스로 순서 있음,**불변형**                 |
| Sequence   | list  | 동적 크기 조정, 반복 순회 가능, 중복 허용, 인덱스로 순서 있음,**가변형** |
| Collection | set   | 반복 순회 가능, 중복 없음, 인덱스 없음, 정렬 안 됨, 가변형               |
| Collection | dict  | 해시 테이블, key-value 매핑, 반복 순회 가능, 컬렉션 타입                 |

```python
# tuple
t1 = tuple()             # empty tuple
t2 = tuple([1, 2, 3])
t3 = tuple({1, 2, 3})
t4 = tuple({'a':1, 'b':2, 'c':3})
t5 = ()                  # empty tuple
t6 = (1,)
t7 = (1, 2, 3)
t8 = 1, 2, 3

# list
l1 = list()              # empty list
l2 = list((1,))
l3 = list((1, 2, 3))
l4 = list({1, 2, 3})
l5 = list({'a':1, 'b':2, 'c':3})
l6 = []
l7 = [1]
l8 = [1, 2, 3]

# set
s1 = set()               # empty set
s2 = set("a")
s3 = set("aabc")
s4 = {"a"}
s5 = {"a", "a", "b", "c"}

# dict
d1 = dict()              # empty dict
d2 = dict(one=1, two=2, three=3)
d3 = dict(zip(['one', 'two', 'three'], [1, 2, 3]))
d4 = dict([('two', 2), ('one', 1), ('three', 3)])
d5 = dict({'three': 3, 'one': 1, 'two': 2})
d6 = dict({'one': 1, 'three': 3}, two=2)
d7 = {}                  # empty dict (실제로는 dict)
d8 = {'one': 1, 'two': 2, 'three': 3}
```

### 1.11 Class

객체를 만드는 수단인 클래스는 생성자와 메서드로 구성된다. 노드 클래스를 자기참조구조체와 대응하여 보여준다.

```python
class Node:
    def __init__(self, newItem, nextNode: 'Node'):
        self.item = newItem
        self.next = nextNode
```

```c
typedef int element;
typedef struct node {
    element item;
    struct node *next;
} Node;
```

## 2. 리스트 추상데이터타입

### 리스트의 연산

- 새로운 항목을 리스트의 끝, 처음, 중간에 추가한다.
- 기존의 항목을 리스트의 임의의 위치에서 삭제한다.
- 모든 항목을 삭제한다.
- 기존의 항목을 대치한다.
- 리스트가 특정한 항목을 가지고 있는지를 살핀다.
- 리스트의 특정위치 항목을 반환한다.
- 리스트 안의 항목 개수를 센다.
- 리스트가 비었는지, 꽉 찼는지를 체크한다.
- 리스트 안의 모든 항목을 표시한다.

### 리스트 ADT

```
객체: n개의 element형으로 구성된 순서있는 모임
연산:
  add_last(list, item)      ::= 맨끝에 요소를 추가한다
  add_first(list, item)     ::= 맨처음에 요소를 추가한다
  add(list, pos, item)      ::= pos 위치에 요소를 추가한다
  delete(list, pos)         ::= pos 위치의 요소를 제거한다
  clear(list)               ::= 리스트의 모든 요소를 제거한다
  replace(list, pos, item)  ::= pos 위치의 요소를 item으로 바꾼다
  is_in_list(list, item)    ::= item이 리스트 안에 있는지를 살핀다
  get_entry(list, pos)      ::= pos 위치의 요소를 반환한다
  get_length(list)          ::= 리스트의 길이를 구한다
  is_empty(list)            ::= 리스트가 비었는지를 검사한다
  is_full(list)             ::= 리스트가 꽉 찼는지를 검사한다
  display(list)             ::= 리스트의 모든 요소를 표시한다
```

### 사용 예

```
addLast(list1, a)    → (a)
addLast(list1, b)    → (a, b)
addLast(list1, c)    → (a, b, c)
add(list1, 1, d)     → (a, d, b, c)
delete(list1, 2)     → (a, d, c)
replace(list1, 1, e) → (a, e, c)
```

## 3. 리스트의 정적 구현

### 3.1 리스트의 구현 방식


| 방식      | 자료구조                    | 장점                                      | 단점                                              |
| ----------- | ----------------------------- | ------------------------------------------- | --------------------------------------------------- |
| 정적 구현 | 배열 또는 리스트            | 구현 간단                                 | 삽입·삭제 시 오버헤드, 항목의 개수 제한(C에서만) |
| 동적 구현 | 연결리스트 (자기참조구조체) | 삽입·삭제가 효율적, 크기가 제한되지 않음 | 구현 복잡                                         |

### 3.2 배열로 구현된 리스트

1차원 배열에 항목들을 순서대로 저장한다. 예: `L = (A, B, C, D, E)`

- **삽입연산**: 삽입위치 다음의 항목들을 한 칸씩 뒤로 이동
- **삭제연산**: 삭제위치 다음의 항목들을 한 칸씩 앞으로 이동

### 3.3 ArrayListType의 구현 (C)

- 항목들의 타입은 `element`로 정의
- `list`라는 1차원 배열에 항목들을 차례대로 저장
- `length`에 항목의 개수 저장

```c
typedef int element;
typedef struct {
    int list[MAX_LIST_SIZE]      // 배열 정의
    int length;                  // 현재 배열에 저장된 항목들의 개수
} ArrayListType;

// 리스트 초기화
void init(ArrayListType *L)
{
    L->length = 0;
}
```

**삽입 연산** — `add` 함수는 먼저 배열이 포화상태인지를 검사하고 삽입위치가 적합한 범위에 있는지를 검사한 뒤, 삽입 위치 다음에 있는 자료들을 한 칸씩 뒤로 이동한다.

```c
// position: 삽입하고자 하는 위치
// item: 삽입하고자 하는 자료
void add(ArrayListType *L, int position, element item)
{
    if( !is_full(L) && (position >= 0) && (position <= L->length) ){
        int i;
        for(i=(L->length-1); i>=position; i--)
            L->list[i+1] = L->list[i];
        L->list[position] = item;
        L->length++;
    }
}
```

**삭제 연산** — 삭제 위치를 검사한 뒤, 삭제위치부터 맨끝까지의 자료를 한 칸씩 앞으로 옮긴다.

```c
// position: 삭제하고자 하는 위치
// 반환값: 삭제되는 자료
element delete(ArrayListType *L, int position)
{
    int i;
    element item;

    if( position < 0 || position >= L->length )
                error("위치 오류");
    item = L->list[position];
    for(i=position; i<(L->length-1); i++)
                L->list[i] = L->list[i+1];
    L->length--;
    return item;
}
```

### 3.4 파이썬 리스트

파이썬 리스트는 동적배열로 구현되어 있다. 크기가 용량보다 작을 때는 그냥 삽입하고, 크기가 용량과 같아지면 다음과 같이 용량을 증가시킨다.

```
Step1: 용량을 확장한 새로운 배열 할당 (예: 기존 배열 용량의 2배)
Step2: 기존의 배열을 새로운 배열에 복사
Step3: 항목을 삽입 (현재 항목의 개수 증가)
Step4: 기존 배열 해제, 리스트로 새 배열 사용
```

**파이썬 리스트의 주요 메소드**


| 메소드           | 설명                                                                              |
| ------------------ | ----------------------------------------------------------------------------------- |
| `l.append(x)`    | 항목을 리스트에 추가                                                              |
| `l.extend(iter)` | 반복 순회가 가능한 항목을 리스트에 추가 (`l += iter`, `l[len(l):] = iter`와 동등) |
| `l.insert(i, x)` | 항목을 리스트의 특정 인덱스 위치에 삽입                                           |
| `l.index(x)`     | 찾는 항목의 인덱스를 반환. 없으면`ValueError`                                     |
| `l.count(x)`     | 찾는 항목의 개수를 반환. 없으면 0                                                 |
| `l.pop(i)`       | 특정 인덱스 위치의 항목을 제거하고 해당 항목을 반환                               |
| `del l[i]`       | 특정 인덱스 위치의 항목을 제거                                                    |
| `l.remove(x)`    | 찾는 값의 첫 번째 항목을 제거. 없으면`ValueError`                                 |
| `l[::-1]`        | 역순 슬라이스 (원본 변경 없음)                                                    |
| `l.reverse()`    | 원본 객체를 역순으로 변경                                                         |

### 3.5 파이썬 ArrayList 클래스

생성자와 메소드로 구성하여 파이썬 리스트를 내부 저장소로 사용하는 ArrayList 클래스를 구현한다.

```python
class ArrayList:
    def __init__(self):                # 생성자
        self.items = []                # 클래스 변수 선언 및 초기화

    def insert(self, pos, elem):
        self.items.insert(pos, elem)
    def delete(self, pos):
        return self.items.pop(ops)
    def isEmpty(self):
        return self.size() == 0
    def getEntry(self, pos):
        return self.items[pos]
    def size(self):
        return len(self.items)
    def clear(self):
        self.items = []                # items는 멤버변수
    def find(self, item):
        return self.items.index(item)
    def replace(self, pos, elem):
        self.items[pos] = elem
    def sort(self):
        self.items.sort()
    def merge(self, lst):
        self.items.extend(lst)
    def display(self, msg='ArrayList:'):
        print(msg, '항목수=', self.items)
```

**테스트 코드**

```python
s = ArrayList()
s.display('파이썬 리스트로 구현한 리스트 테스트')
s.insert(0, 10);          s.insert(0, 20);          s.insert(1, 30)
s.insert(s.size(), 40);   s.insert(2, 50)
s.display("파이썬 리스트로 구현한 List(삽입x5): ")
s.sort()
s.display("파이썬 리스트로 구현한 List(정렬후): ")
s.replace(2, 90)
s.display("파이썬 리스트로 구현한 List(교체x1): ")
s.delete(2);              s.delete(s.size() - 1);   s.delete(0)
s.display("파이썬 리스트로 구현한 List(삭제x3): ")
lst = [1, 2, 3]
s.merge(lst)
s.display("파이썬 리스트로 구현한 List(병합+3): ")
s.clear()
s.display("파이썬 리스트로 구현한 List(정리후): ")
```

## 실습 코드


| 파일                                       | 설명                                   |
| -------------------------------------------- | ---------------------------------------- |
| [`code/array_list.py`](code/array_list.py) | 파이썬`ArrayList` 클래스 + 테스트 코드 |
