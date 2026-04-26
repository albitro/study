# 스택(Stacks)

## 목차

- [핵심 요약](#핵심-요약)
- [1. 스택과 큐의 자료구조](#1-스택과-큐의-자료구조)
- [2. 스택 추상데이터타입](#2-스택-추상데이터타입)
- [3. 스택의 정적 구현](#3-스택의-정적-구현)
- [4. 스택의 동적 구현](#4-스택의-동적-구현)
- [5. 스택의 응용](#5-스택의-응용)
- [실습 코드](#실습-코드)

## 핵심 요약

- 스택은 리스트의 한쪽(top)에서만 삽입·삭제하는 LIFO 자료구조이고, 큐는 한쪽(rear)에서 넣고 반대쪽(front)에서 빼는 자료구조다.
- 스택의 정적 구현은 1차원 배열과 `top` 인덱스(초기값 -1)로 만들고, 동적 구현은 연결 리스트로 만들어 크기 제한을 없앤다.
- 스택의 대표 응용은 후위식 변환과 계산이며, 후위식은 괄호와 연산자 우선순위 없이 왼쪽부터 기계적으로 계산할 수 있다.
- 후위식 변환은 연산자에 대해 `isp[stack[top]] < icp[token]`이면 push, 아니면 pop until 조건 성립까지의 규칙을 따른다.

---

## 1. 스택과 큐의 자료구조

### 1.1 스택(Stack)과 큐(Queue)

스택은 한쪽 끝에서 push/pop이 일어나는 자료구조이고, 큐는 한쪽 끝(rear)에서 enqueue, 반대쪽 끝(front)에서 dequeue가 일어나는 자료구조다.

### 1.2 리스트, 스택과 큐

스택과 큐는 리스트 자료구조의 특별한 경우이다.


| 자료구조 | 순서 | 삽입          | 삭제          |
| ---------- | ------ | --------------- | --------------- |
| 리스트   | 있다 | 어느 곳에서나 | 어느 곳에서나 |
| 스택     | 있다 | 한쪽(top)     | 한쪽(top)     |
| 큐       | 있다 | 한쪽(rear)    | 반대쪽(front) |

### 1.3 스택

스택 S = (a<sub>0</sub>, ···, a<sub>n-1</sub>)

- a<sub>0</sub>: bottom 원소
- a<sub>n-1</sub>: top 원소
- a<sub>i</sub>: 스택 원소 (0 < i < n-1), i+1번째 원소

스택에서의 원소의 삽입과 삭제:

- 삽입은 리스트의 마지막에, 삭제도 리스트의 마지막에서 행한다.
- **Last-In-First-Out (LIFO)** 자료구조

```
A           push(A)
↑ top
A B         push(B)
  ↑ top
A B C       push(C)
    ↑ top
A B         pop()
  ↑ top
A B D       push(D)
    ↑ top
```

### 1.4 스택의 사용: 입력과 역순의 출력이 필요한 경우

- 함수호출
- 수식의 계산
- 에디터에서 되돌리기(undo) 기능
- 웹브라우저에서 뒤로가기(backward) 기능

---

## 2. 스택 추상데이터타입

### 2.1 스택 ADT

- 객체: n개의 element형의 요소들의 선형 리스트
- 연산:
  - `create()` ::= 스택을 생성한다.
  - `is_empty(s)` ::= 스택이 비어있는지를 검사한다.
  - `is_full(s)` ::= 스택이 가득 찼는가를 검사한다.
  - `push(s, e)` ::= 스택의 맨 위에 요소 e를 추가한다.
  - `pop(s)` ::= 스택의 맨 위에 있는 요소를 삭제한다.
  - `peek(s)` ::= 스택의 맨 위에 있는 요소를 삭제하지 않고 반환한다.

### 2.2 스택의 연산

```
top()     : 스택의 맨 위에 있는 데이터 값을 반환한다.
push()    : 스택에 데이터를 삽입한다.
pop()     : 스택에서 데이터를 삭제하여 반환한다.
isempty() : 스택에 원소가 없으면 'true' 있으면 'false' 값 반환
isfull()  : 스택에 원소가 없으면 'false' 있으면 'true' 값 반환
```

---

## 3. 스택의 정적 구현

### 3.1 스택의 생성

1차원 배열의 사용:

```c
#define MAX_STACK_SIZE 100
int stack[MAX_STACK_SIZE];
int top = -1;
/* top의 초기 값은 스택이 비어있을 때 -1이다. */
```

### 3.2 스택의 삽입: PUSH

```c
void push(int item)
{
    if(top >= MAX_STACK_SIZE - 1) {
        stack_full();
        return;
    }
    stack[++top] = item;
    // top++; stack[top] = item;
}
```

### 3.3 스택의 삭제: POP

```c
int pop( ) {
    if(top == -1)
        return stack_empty();
    return stack[top--];
    // int x; x = stack[top]; top--; return x;
}
```

### 3.4 스택의 검사

```c
// 스택이 비어있는지 검사하는 함수
int isempty()
{ if( top < 0 ) return(1); else return(0); }

// 스택이 가득 차 있는지 검사하는 함수
int isfull()
{ if ( top >= MAX_STACK_SIZE -1 ) return(1);
  else return(0); }
```

### 3.5 스택의 구현 using C

```c
#include <stdio.h>
#define MAX_STACK_SIZE 100

int stack[MAX_STACK_SIZE];
int top = -1;

void push(int item)
{
    if(top >= MAX_STACK_SIZE - 1) {
        printf("stack_full()\n");
        return;
    }
    stack[++top] = item;
}

int pop() {
    if(top == -1)
    {
        printf("stack_empty()\n"); exit();
    }
    return stack[(top)--];
}

int isempty()
{ if( top == -1 ) return(1); else return(0); }

int isfull()
{ if ( top >= MAX_STACK_SIZE -1 ) return(1);
  else return(0); }

int main()
{
    int e;
    push(20);
    push(40);
    push(60);

    printf(" Begin Stack Test ...\n");

    while(!isempty())
    {
        e = pop();
        printf("value = %d\n", e);
    }
}
```

실행 결과:

```
Begin stack test ...
element = 60
element = 40
element = 20
stack is empty!!
```

### 3.6 스택의 구현 using Python

`code/static_stack.py` 참고. 파이썬 리스트를 내부 컨테이너로 사용한 `ListStack_` 클래스를 구현한다.

---

## 4. 스택의 동적 구현

### 4.1 Linked List로 구현한 스택

연결된 스택(linked stack): 연결리스트를 이용하여 구현한 스택.

- 장점: 크기가 제한되지 않음
- 단점: 구현이 복잡하고 삽입이나 삭제 시간이 오래 걸린다.

### 4.2 스택의 생성

```c
typedef int element;        // 요소의 타입

typedef struct StackNode {  // 노드의 타입
    element item;
    struct StackNode *link;
} StackNode;

typedef struct {            // 연결된 스택의 관련 데이터
    StackNode *top;
} LinkedStackType;
```

### 4.3 스택의 삽입

```c
// 삽입 함수
void push(LinkedStackType *s, element item)
{
    StackNode *temp=(StackNode *)malloc(sizeof(StackNode));
    if( temp == NULL ){
        fprintf(stderr, "메모리 할당에러\n");
        return;
    }
    else{
        temp->item = item;
        temp->link = s->top;
        s->top = temp;
    }
}
```

### 4.4 스택의 삭제

```c
// 삭제 함수
element pop(LinkedStackType *s)
{
    if( is_empty(s) ) {
        fprintf(stderr, "스택이 비어있음\n");
        exit(1);
    }
    else{
        StackNode *temp=s->top;
        int item = temp->item;
        s->top = s->top->link;
        free(temp);
        return item;
    }
}
```

### 4.5 스택의 구현 using C

실행 결과:

```
The push element is 20.
The push element is 40.
The push element is 60.
Begin stack test ...
The pop element is 60.
The pop element is 40.
The pop element is 20.
```

### 4.6 스택의 구현 using Python

`code/linked_stack.py` 참고. `Node_`, `LinkedList_`, `LinkedListStack_` 세 클래스를 정의하여 동적 스택을 구현한다.

---

## 5. 스택의 응용

### 5.1 수식의 계산

후위표기식(postfix notation, 후위식): 후위식은 연산자를 피연산자의 뒤에 놓는 방법이다. 스택의 응용의 예이며 수식의 계산은 계산기에서나 컴퓨터 프로그래밍을 할 때 자주 나타난다.

다음 수식을 사람이 계산하는 과정:

```
x = a/b - c + d*e - a*c   (중간결과는 temp에 기록한다)
  = (a/b) - c + d*e - a*c
  = (temp1) - c + d*e - a*c
  = (temp1) - c + (temp2) - a*c
  = (temp1) - c + (temp2) - (temp3)
  = (temp4) + (temp2) - (temp3)
  = (temp5) - (temp3)
  = (temp6)
```

사람은 안쪽 괄호부터 계산을 해 나간다:

```
x = ((((a/b) - c) + (d*e)) - (a*c))
```

### 5.2 사람과 컴퓨터의 수식 계산

**사람의 수식 계산**

- 연산자의 우선 순위를 정한다. 우선순위가 같으면 왼쪽부터인지 오른쪽부터인지 정한다. (`/`, `*`, `+`, `-` 연산자는 왼쪽부터이지만, 지수 연산자는 오른쪽 부터이다.)
- 복잡하면 괄호를 사용하여 계산하며 중간 결과를 저장한다. 예를 들면, `(((A/(B**C)) + (D*E)) - (A*C))`

**컴퓨터의 수식 계산**

중간 과정을 줄이고 한번에 왼쪽에서 오른쪽으로 계산할 수 있는 방법을 개발하였다.

1. 수식을 후위표기법(postfix notation, 후위식)으로 바꾼다.
2. 후위식을 계산한다.

### 5.3 연산자 우선 순위

#### C


| 우선순위  | 연산자 유형        | 연산자                                            |
| ----------- | -------------------- | --------------------------------------------------- |
| 1 (높다)  | 괄호, 배열, 구조체 | `()` `[]` `.` `->`                                |
| 2         | 단항 연산          | `-` `!` `~` `++` `--` `(type)` `&` `*` `sizeof()` |
| 3         | 산술연산 (승제)    | `*` `/` `%`                                       |
| 4         | 산술연산 (가감)    | `+` `-`                                           |
| 5         | 비트 이동 연산     | `>>` `<<`                                         |
| 6         | 관계연산 (비교)    | `<` `<=` `>` `>=`                                 |
| 7         | 관계연산 (등가)    | `==` `!=`                                         |
| 8         | 비트 논리 연산     | `&` `|` `^`                                       |
| 9         | 논리 연산          | `&&` `||`                                         |
| 10        | 조건 연산          | `?:`                                              |
| 11        | 대입 연산          | `=` `+=` `-=` `*=` `/=` `%=` `>>=` `<<=`          |
| 12 (낮다) | 나열 연산          | `,`                                               |

#### Python


| 연산자                                          | 설명                                    |
| ------------------------------------------------- | ----------------------------------------- |
| `**`                                            | 지수 연산자                             |
| `~`, `+`, `-`                                   | 단항 연산자                             |
| `*`, `/`, `%`, `//`                             | 곱셈, 나눗셈, 나머지 연산자, 나눗셈(몫) |
| `+`, `-`                                        | 덧셈, 뺄셈                              |
| `>>`, `<<`                                      | 비트 이동 연산자                        |
| `&`                                             | 비트 AND 연산자                         |
| `^`, `|`                                        | 비트 XOR 연산자, 비트 OR 연산자         |
| `<=`, `<`, `>`, `>=`                            | 비교 연산자                             |
| `<>`, `==`, `!=`                                | 동등 연산자                             |
| `=`, `%=`, `/=`, `//=`, `-=`, `+=`, `*=`, `**=` | 대입 연산자                             |
| `is`, `is not`                                  | 아이덴티티 연산자                       |
| `in`, `not in`                                  | 소속 연산자                             |
| `not`, `or`, `and`                              | 논리 연산자                             |

### 5.4 후위식 변환

사람이 사용하는 수식의 표기 방법은 **중위표기식(infix notation, 중위식)** 이라고 한다. 중위식은 연산자(operator)를 피연산자(operand) 가운데 놓는 방법이다.

```
3 * 5  =>  (피연산자) (연산자) (피연산자)
```

후위식은 연산자를 피연산자 뒤에 놓고 표기하는 방법이다.

```
3 5 *  =>  (피연산자) (피연산자) (연산자)
```

후위식으로 놓으면 괄호 없이도 계산 순서가 일정하다.

- 예 1) `3 * 5 + 4`
  - 중위식 → `3 * 5 + 4`
  - 후위식 → `3 5 * 4 +`
- 예 2) `3 * (5 + 4)`
  - 중위식 → `3 * (5 + 4)` (괄호가 필요하다. 5+4를 먼저 계산하려면)
  - 후위식 → `3 5 4 + *` (괄호가 필요 없다)

**후위식 계산 예 1**: `3 * 5 + 4 = 3 5 * 4 +`

```
1단계) 3 5 * 4 +
2단계) 15 4 +    => 3 5 * 를 계산하여 저장한다.
3단계) 19        => 15 4 + 를 계산한다.
```

**후위식 계산 예 2**: `3 * (5 + 4) = 3 5 4 + *`

```
1단계) 3 5 4 + *
2단계) 3 9 *     => 5 4 + 를 계산한다.
3단계) 27        => 3 9 * 를 계산한다.
```

연산자가 나올 때까지 읽고 연산자의 앞에 있는 피연산자 두 개로 계산하고 그 자리에 저장한다.

**중위식 → 후위식 변환 예시**


| 중위표기(infix)                   | 후위표기(postfix)           |
| ----------------------------------- | ----------------------------- |
| `2 + 3 * 4`                       | `2 3 4 * +`                 |
| `a * b + 5`                       | `a b * 5 +`                 |
| `(1 + 2) * 7`                     | `1 2 + 7 *`                 |
| `a*b/c`                           | `a b * c /`                 |
| `(a / (b - c + d)) * (e - a) * c` | `a b c - d + / e a - * c *` |
| `a/b - c + d * e - a * c`         | `a b / c - d e * + a c * -` |

쉽게 바꾸는 방법: 중위식에 괄호를 친 다음 연산자를 괄호 뒤로 옮긴 후 괄호를 지운다.

```
예) (((A / (B*C)) + (D*E)) - (A*C))
=>  A B C * / D E * + A C * -
```

### 5.5 후위식 변환 알고리즘

수식을 읽어 연산자와 피연산자에 따라 다음과 같이 처리한다.

1. 피연산자는 출력한다.
2. 연산자는 앞 연산자(스택의 맨 위)를 살펴서 출력하거나 대기한다. (스택에 넣는다, 대기 된 자료들은 나중에 대기 된 연산자가 먼저 나온다.)
3. 연산자의 대기(스택에 push)여부는 연산자간의 우선순위에 따른다.

**연산자에 대한 스택 처리: in-stack precedence(isp), incoming precedence(icp)**

```
       top → ┐                      ┌── token
             │                      │
             stack ── 비교 ────────┘
       "in-stack precedence"   "in-coming precedence"
       스택에 있는 연산자의      입력될 때 연산자의
       우선순위                  우선순위
```

- `if (isp[stack[top]] < icp[token])`, `push()`
  - 입력된 연산자가 스택의 맨 위 연산자보다 우선순위가 클 경우
- `if (isp[stack[top]] >= icp[token])`, `pop()` until `(isp[stack[top]] < icp[token])`
  - 입력된 연산자가 스택의 맨 위 연산자보다 우선순위가 작거나 같을 경우

**입력단계별 스택 변화: 괄호가 없는 경우 (`a+b*c`)**


| 토큰(입력) | 스택의 모양 | top 변수의 값 | 출력        |
| ------------ | ------------- | --------------- | ------------- |
| `a`        |             | -1            | `a`         |
| `+`        | `+`         | 0             | `a`         |
| `b`        | `+`         | 0             | `a b`       |
| `*`        | `+ *`       | 1             | `a b`       |
| `c`        | `+ *`       | 1             | `a b c`     |
| `eos(끝)`  |             | -1            | `a b c * +` |

**입력단계별 스택 변화: 괄호가 있는 경우 (`a*(b+c)*d`)**

후위표기법으로 표기하면 괄호가 없어진다.

- 왼쪽괄호 - 무조건 스택에 넣는다.
- 오른쪽 괄호의 처리 - 왼쪽 괄호가 나올 때까지 스택에서 pop 한다.


| 토큰  | 스택의 모양 | top 변수의 값 | 출력            |
| ------- | ------------- | --------------- | ----------------- |
| `a`   |             | -1            | `a`             |
| `*`   | `*`         | 0             | `a`             |
| `(`   | `* (`       | 1             | `a`             |
| `b`   | `* (`       | 1             | `a b`           |
| `+`   | `* ( +`     | 2             | `a b`           |
| `c`   | `* ( +`     | 2             | `a b c`         |
| `)`   | `*`         | 0             | `a b c +`       |
| `*`   | `*`         | 0             | `a b c + *`     |
| `d`   | `*`         | 0             | `a b c + * d`   |
| `eos` |             | -1            | `a b c + * d *` |

**후위식 변환 함수 using C**

```c
/* 수식 계산을 위한 프로그램 선언 부분 */
#define MAX_STACK_SIZE 100  /* maximum stack size */
#define MAX_EXPR_SIZE 100   /* max size of expression */

/* 열거형 타입 precedence 선언 */
typedef enum {lparen, rparen, plus, minus,
              times, divide, mode, eos, operand
} precedence;

precedence stack[MAX_STACK_SIZE]; /* 스택선언 */
char expr[MAX_EXPR_SIZE];         /* 입력 문자열 */

static int isp[] = {0,19,12,12,13,13,13,0};
static int icp[] = {20,19,12,12,13,13,13,0};

/* 입력에서 토큰을 받아들이는 함수 */
precedence get_token(char *symbol, int *n) {
    *symbol = expr[(*n)++];
    switch(*symbol) {
        case '(': return lparen;
        case ')': return rparen;
        case '+': return plus;
        case '-': return minus;
        case '/': return divide;
        case '*': return times;
        case '%': return mod;
        case ' ': return eos;
        default: return operand;
    }
}

/* 중위표기를 후위표기로 바꾸는 함수 */
void postfix(void) {
    char symbol;
    precedence token;
    int n = 0;
    int top = 0;
    stack[0] = eos;
    for(token = get_token(&symbol, &n); token != eos;
        token = get_token(&symbol, &n)) {
        if(token == operand) printf("%c", symbol);
        else if(token == rparen) {
            while(stack[top] != lparen)
                print_token(pop());
            pop();
        }
        else {
            while(isp[stack[top]] >= icp[token])
                print_token(pop());
            push(token);
        }
    }
    while((token = pop()) != eos)
        print_token(token);
    printf("\n");
}
```

### 5.6 후위식 계산

후위식(postfix notation)의 계산은 괄호(parenthesis)가 필요 없고 연산자 우선순위(precedence)가 필요 없다.

**프로그램 복잡도**

- 시간복잡도: O(n), n은 수식 기호의 개수
- 공간복잡도: O(n), n은 연산자의 수

**후위식 계산 예**: `6 2 / 3 - 4 2 * +`


| 토큰 | 스택의 모양 | top 변수의 값 |
| ------ | ------------- | --------------- |
| `6`  | `6`         | 0             |
| `2`  | `6 2`       | 1             |
| `/`  | `3`         | 0             |
| `3`  | `3 3`       | 1             |
| `-`  | `0`         | 0             |
| `4`  | `0 4`       | 1             |
| `2`  | `0 4 2`     | 2             |
| `*`  | `0 8`       | 1             |
| `+`  | `8`         | 0             |

**후위식 계산 알고리즘**

```
get_token() 함수
/* 수식에서 토큰을 한 개씩 읽는 프로그램 */

eval()
{
    if the token is operand
        push to the stack
    otherwise
        1) pop two operands from the stack
        2) perform the specified operation
        3) push the result back on the stack
}
```

**후위식 계산 함수 using C**

```c
/* 후위표기식을 계산하는 프로그램 */
int eval(void)
{
    precedence token;
    char symbol;
    int op1, op2;
    int n = 0;
    int top = -1;
    token = get_token(&symbol, &n);
    while (token != eos) {
        if(token == operand)
            push(symbol-'0');
        else {
            op2 = pop();
            op1 = pop();
            switch(token) {
            case plus: push(op1 + op2); break;
            case minus: push(op1 - op2); break;
            case times: push(op1 * op2); break;
            case divide: push(op1 / op2); break;
            case mod: push(op1 % op2);
            } }
        token = get_token(&symbol, &n); }
    return pop();
}
```

### 5.7 후위식 변환과 계산: 실행 예

```
Infix expression is 7*(4+2-3)/3.
Postfix expression is 742+3-*3/.
The result of calculation is 7.
```

---

## 실습 코드


| 파일                   | 설명                                                                          |
| ------------------------ | ------------------------------------------------------------------------------- |
| `code/static_stack.py` | 파이썬 리스트를 사용한 정적 스택`ListStack_`               |
| `code/linked_stack.py` | `Node_`/`LinkedList_` 위에 구현한 동적 스택 `LinkedListStack_` |
| `code/postfix_calc.py` | `ListStack_`을 활용한 후위식 변환·계산 `PostfixCalc`        |
