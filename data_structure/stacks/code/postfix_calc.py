from static_stack import ListStack_


class PostfixCalc(object):
    def __init__(self, expr=""):
        self.__lstack = ListStack_()
        self.__expr = expr
        self.__precedence = {"(": 0, ")": 0, "+": 1, "-": 1, "*": 2, "/": 2}

    @property
    def expr(self):
        return self.__expr

    @expr.setter
    def expr(self, arg):
        self.__expr = arg

    def __is_op(self, ch):
        return ch in "+-*/"

    def __char_to_int(self, ch):
        return ord(ch) - ord("0")

    def __is_less_equal(self, op):
        pr1 = self.__precedence[op]
        pr2 = self.__precedence[self.__lstack.top]
        return True if pr1 <= pr2 else False

    def infix_to_postfix(self, infix):
        postfix = []
        for ch in infix:
            if ch == "(":
                self.__lstack.push(ch)
            elif ch == ")":
                while not self.__lstack.is_empty():
                    op = self.__lstack.pop()
                    if op == "(":
                        break
                    else:
                        postfix.append(op)
            elif self.__is_op(ch):
                while not self.__lstack.is_empty():
                    if self.__is_less_equal(ch):
                        postfix.append(self.__lstack.pop())
                    else:
                        break
                self.__lstack.push(ch)
            else:
                postfix.append(ch)

        while not self.__lstack.is_empty():
            postfix.append(self.__lstack.pop())
        return " ".join(postfix)

    def calculate(self):
        is_digit_prev = False
        for ch in self.__expr:
            if ch.isdigit():
                if is_digit_prev:
                    temp = self.__lstack.pop()
                    temp = temp * 10 + self.__char_to_int(ch)
                    self.__lstack.push(temp)
                else:
                    self.__lstack.push(self.__char_to_int(ch))
                is_digit_prev = True
            elif self.__is_op(ch):
                digit2 = self.__lstack.pop()
                digit1 = self.__lstack.pop()
                op = {
                    "+": digit1 + digit2,
                    "-": digit1 - digit2,
                    "*": digit1 * digit2,
                    "/": digit1 // digit2,
                }
                self.__lstack.push(op[ch])
                is_digit_prev = False
            else:
                is_digit_prev = False
        return self.__lstack.pop()


if __name__ == "__main__":
    infix = "15 * ( 25 + 3 - 10 ) / 3"
    calc = PostfixCalc()
    print(calc.infix_to_postfix(infix))

    expression = "15 25 3 + 10 - * 3 /"
    calc = PostfixCalc(expression)
    print(f"{calc.expr} => {calc.calculate()}")

    calc.expr = "10 5 * 3 - 12 + 3 *"
    print(f"{calc.expr} => {calc.calculate()}")


# ---
# 실행 결과 고찰
#
# 기대: infix_to_postfix("15 * ( 25 + 3 - 10 ) / 3") => "15 25 3 + 10 - * 3 /"
# 실제: "1 5       2 5     3   +   1 0   -   *   3 /"
# 추정 원인:
#   1. 입력 중위식의 공백 문자를 별도로 처리하지 않아, 공백이 피연산자도
#      연산자도 괄호도 아닌 분기의 else로 흘러 postfix.append(ch)로 추가된다.
#   2. 두 자리 수("15", "25", "10")의 각 자릿수도 한 글자씩 분리되어 따로
#      append되므로 "1 5", "2 5", "1 0" 처럼 쪼개진다. infix_to_postfix는
#      자릿수를 이어 붙이는 로직이 없고, 다중 자릿수 처리는 calculate의
#      is_digit_prev 분기에만 들어 있다.
#   3. 두 효과가 합쳐져, 연속된 글자/공백이 모두 개별 토큰으로 취급되어
#      과도한 공백이 섞인 출력이 된다.
# (코드를 수정하지 않고 원인 추정만 남긴다)
