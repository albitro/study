# Topic 1: Language Models (n-gram)

> 확률적 언어 모델의 출발점인 **n-gram language model**을 정의, 생성, 평가, 평활화 네 축으로 정리한다.

---

## 목차

1. [n-gram Language Model이란?](#1-n-gram-language-model-이란)
2. [n-gram의 종류와 Chain Rule](#2-n-gram-의-종류와-chain-rule)
3. [확률 추정 — MLE와 차원의 저주](#3-확률-추정--mle-와-차원의-저주)
4. [Markov Assumption](#4-markov-assumption)
5. [언어 모델로부터 문장 생성하기](#5-언어-모델로부터-문장-생성하기)
6. [언어 모델 평가 — Extrinsic vs Intrinsic, Perplexity](#6-언어-모델-평가--extrinsic-vs-intrinsic-perplexity)
7. [Sparsity, Zipf's Law, Smoothing의 필요성](#7-sparsity-zipfs-law-smoothing-의-필요성)
8. [Smoothing 기법](#8-smoothing-기법)

---

## 1. n-gram Language Model 이란?

**언어 모델(language model, LM)**은 단어 시퀀스 $w_1, w_2, \dots, w_n$ 에 결합 확률(joint probability)을 부여하는 확률 모델이다.

$$
P(w_1, w_2, \dots, w_n)

$$

이 확률은 "주어진 문장(혹은 문서)이 얼마나 그럴듯한가?" 라는 질문에 대한 정량적 답이다. 이 정의 위에서 언어 모델은 **다음 단어 예측**, **자동 완성**, **기계 번역의 디코딩**, **음성 인식의 후처리** 등 광범위한 응용으로 확장된다.

n-gram이라는 이름은 모델이 **연속된 $n$개의 토큰**(단어 혹은 문자) 을 기본 단위로 삼기 때문에 붙었다.


| 종류              |   $n$   | 예: "I love NLP"     |
| ------------------- | :-------: | ---------------------- |
| Unigram           |    1    | `I`, `love`, `NLP`   |
| Bigram            |    2    | `I love`, `love NLP` |
| Trigram           |    3    | `I love NLP`         |
| 4-gram, 5-gram... | $\geq$4 | 더 긴 연속 토큰 묶음 |

---

## 2. n-gram의 종류와 Chain Rule

확률의 **체인 룰(chain rule)**에 의해 임의의 결합 확률은 조건부 확률의 곱으로 정확히 분해된다.

$$
P(w_1, w_2, \dots, w_n) \;=\; P(w_1)\, P(w_2 \mid w_1)\, P(w_3 \mid w_1, w_2) \cdots P(w_n \mid w_1, \dots, w_{n-1})

$$

예를 들어 "the cat sat on the mat"의 확률은

$$
P(\text{the}) \cdot P(\text{cat}\mid\text{the}) \cdot P(\text{sat}\mid\text{the cat}) \cdot P(\text{on}\mid\text{the cat sat}) \cdots

$$

로 풀어진다. 문제는 $P(w_n \mid w_1, \dots, w_{n-1})$ 같은 **임의의 긴 history에 대한 조건부 확률**을 직접 추정하기가 사실상 불가능하다는 점이다.

n-gram 모델은 이 history를 **마지막 $k$개의 토큰으로 잘라내는 근사**로 이 문제를 우회한다.

---

## 3. 확률 추정 — MLE와 차원의 저주

### 3.1 카운트로 추정하기 (MLE)

조건부 확률은 코퍼스에서 다음과 같이 **상대 빈도(relative frequency)**로 추정한다 (maximum likelihood estimate, MLE):

$$
P(\text{sat} \mid \text{the cat}) = \frac{\#(\text{the cat sat})}{\#(\text{the cat})}

$$

여기서 $\#(\cdot)$는 학습 코퍼스 내 해당 토큰열의 출현 횟수이다. 즉 **표본 공간 = 코퍼스 = 학습 데이터**이고, 이 코퍼스가 유한하다는 사실이 이후 모든 문제의 근원이 된다.

### 3.2 왜 history를 자를 수밖에 없는가?

어휘 크기를 $V$라 하면, 길이 $n$의 단어열 가짓수는

$$
\boxed{V^n}

$$

이다. 일반적인 영어 어휘 $V \approx 4 \times 10^4$ 일 때, 길이 11짜리 문장만 해도

$$
(4 \times 10^4)^{11} \approx 4 \times 10^{50}

$$

가지로, **지구상 원자 수($\sim 10^{50}$)와 같은 자릿수** 다. 이 모든 시퀀스의 확률을 따로 추정하는 것은 원리적으로 불가능하다.

---

## 4. Markov Assumption

**마르코프 가정(Markov assumption)**은 다음 단어가 **최근 $k$개 단어에만** 의존한다고 단순화한다.

$$
P(w_i \mid w_1, \dots, w_{i-1}) \;\approx\; P(w_i \mid w_{i-k}, \dots, w_{i-1})

$$

이를 전체 시퀀스에 적용하면

$$
\boxed{\,P(w_1, \dots, w_n) \;\approx\; \prod_{i=1}^{n} P(w_i \mid w_{i-k}, \dots, w_{i-1})\,}

$$

이며, 이때 추정해야 할 카운트는 최대 $(k+1)$-gram까지로 제한된다. 모델별로 정리하면:


| 모델    | 차수 $k$ | 분해식                                 |
| --------- | :--------: | ---------------------------------------- |
| Unigram |    0    | $\prod_i P(w_i)$                       |
| Bigram  |    1    | $\prod_i P(w_i \mid w_{i-1})$          |
| Trigram |    2    | $\prod_i P(w_i \mid w_{i-2}, w_{i-1})$ |

$n$이 클수록 더 풍부한 문맥을 보지만, 카운트해야 할 n-gram의 수가 $V^{n}$으로 폭증해 **희소성(sparsity)**도 같이 커진다. **표현력 vs 추정 가능성** 사이의 trade-off이다.

---

## 5. 언어 모델로부터 문장 생성하기

### 5.1 순차 샘플링

bigram 모델 $P(w_i \mid w_{i-1})$이 있으면 문장을 한 토큰씩 만들어낼 수 있다.

1. $w_1 \sim P(w \mid \langle s \rangle)$
2. $w_2 \sim P(w \mid w_1)$
3. $w_3 \sim P(w \mid w_2)$
4. ... $\langle /s \rangle$ 가 나올 때까지 반복

trigram이라면 매 step 마다 직전 두 단어를 조건으로 둔다. **n 이 클수록 응집도(coherence)**가 좋아지지만, 학습 데이터에 과적합되어 **단순 복붙(memorization)**으로 흐를 위험도 커진다.

### 5.2 다음 단어를 고르는 세 가지 방법

다음 단어 후보의 확률 분포를 얻은 뒤 실제로 어떤 토큰을 뽑을지는 별개 문제다. 여기서는 세 가지를 비교한다.


| 방법                           | 정의                                              | 특성                                          |
| -------------------------------- | --------------------------------------------------- | ----------------------------------------------- |
| **Greedy**                     | $w = \arg\max_{w \in V} P(w \mid \text{context})$ | 결정적, 안정적이나 반복, 진부                 |
| **Top-$k$ sampling**           | 확률 상위 $k$개만 남기고 재정규화 후 샘플         | 다양성 확보,$k$ 고정이라 분포 모양에 둔감     |
| **Top-$p$ (nucleus) sampling** | 누적확률이$p$를 넘는 최소 집합에서 샘플           | 분포가 뾰족하면 적게, 평평하면 많이 — 적응적 |

```
Token   Prob
for     0.40
to      0.25
with    0.17
and     0.13
by      0.05
```

위 분포에서 **Top-3**은 `{for, to, with}` 를, **Top-$p$ ($p=0.6$)**는 `{for, to}` 를 후보로 잡는다 ($0.40 + 0.25 = 0.65 \geq 0.6$).

---

## 6. 언어 모델 평가 — Extrinsic vs Intrinsic, Perplexity

### 6.1 두 가지 평가 관점


| 분류          | 방식                                                             | 장단점                                                   |
| --------------- | ------------------------------------------------------------------ | ---------------------------------------------------------- |
| **Extrinsic** | LM을 다운스트림 태스크(번역, 요약 등) 에 끼우고 그 정확도로 비교 | 실제 유용성 직접 측정, but **느리고 비용 큼**, 간접 신호 |
| **Intrinsic** | LM 자체의 통계적 품질을 직접 측정 (대표 지표:**perplexity**)     | 빠르고 재현 가능, but task 성능과 항상 일치하진 않음     |

n-gram시대에는 perplexity가 사실상 표준이었고, 현대 LLM도 학습/검증 중 perplexity를 핵심 모니터링 지표로 사용한다 (다만 GLUE, SuperGLUE, KLUE, MMLU 같은 종합 벤치마크가 extrinsic 평가를 보강).

### 6.2 Perplexity 정의

테스트 코퍼스 $w_1, \dots, w_n$ 에 대해 LM 이 부여하는 결합확률을 $P(w_1, \dots, w_n)$ 이라 할 때,

$$
\boxed{\;\mathrm{ppl}(S) \;=\; P(w_1, \dots, w_n)^{-\frac{1}{n}} \;=\; \exp\!\left(-\frac{1}{n} \sum_{i=1}^{n} \log P(w_i \mid w_1, \dots, w_{i-1})\right)\;}

$$

지수부의 음의 평균 로그우도가 곧 **cross-entropy**다. 즉 perplexity를 줄이는 것은 cross-entropy를 줄이는 것이고, 이는 곧 **테스트 코퍼스의 우도를 최대화** 하는 것이다.

### 6.3 직관

만약 $k$-gram 모델이 어휘 위에 균등 분포 $P(w \mid \cdot) = 1/V$를 부여한다면,

$$
\mathrm{ppl} = \exp\!\left(-\frac{1}{n} \sum_i \log \tfrac{1}{V}\right) = \exp(\log V) = V

$$

즉 **perplexity는 "모델이 매 step 마다 평균적으로 몇 개의 단어 사이에서 헷갈리는가"**의 척도다. 낮을수록 좋다.

### 6.4 WSJ 결과

학습 38M / 테스트 1.5M (둘 다 Wall Street Journal)로 보고된 결과:


| n-gram | unigram | bigram | trigram |
| :------: | :-------: | :------: | :-------: |
|  ppl  |   962   |  170  |   109   |

$n$을 늘릴수록 perplexity가 떨어지지만 diminishing returns이 뚜렷하다.

---

## 7. Sparsity, Zipf's Law, Smoothing 의 필요성

### 7.1 0 확률 문제

학습 코퍼스에 **단 한 번도 등장하지 않은 n-gram**이 테스트에 있으면 그 항의 확률은 0 이고, 곱셈으로 이루어진 문장 확률 전체가 0 이 된다. 그러면 cross-entropy가 $+\infty$ 가 되어 **perplexity가 정의되지 않는다**.

```
학습 = Google news,   테스트 = Shakespeare
P(affray voice doth us) = 0   ⇒   P(test corpus) = 0   ⇒   ppl = ∞
```

### 7.2 왜 항상 일어나는가? — Zipf's Law

자연어는 단어 빈도가 순위(rank)의 역수에 비례하는 **Zipf 분포**를 따른다.

$$
\text{frequency} \;\propto\; \frac{1}{\text{rank}}

$$

상위 몇 개 단어(`the`, `of`, `and`, ...)가 압도적으로 자주 등장하고, 그 외 대다수 단어는 **롱테일(long tail)**에 흩어져 있다. 코퍼스를 아무리 키워도 한 번도 못 본 표현은 항상 새로 등장한다. 따라서 **smoothing**은 옵션이 아니라 필수다.

### 7.3 Smoothing의 큰 그림


| 기법              | 핵심 아이디어                                                              |
| ------------------- | ---------------------------------------------------------------------------- |
| Additive(Laplace) | 모든 카운트에 작은 양 $\alpha$를 더해 0을 없앤다                           |
| Discounting       | 본 적 있는 n-gram에서 확률을 조금씩 떼어내, 본 적 없는 n-gram들에 나눠준다 |
| Interpolation     | 차수가 다른 여러 n-gram을 가중평균한다                                     |

---

## 8. Smoothing 기법

### 8.1 Additive (Laplace / add-$\alpha$) Smoothing

가장 단순한 평활화. bigram의 경우

$$
P(w_i \mid w_{i-1}) = \frac{C(w_{i-1}, w_i) + \alpha}{C(w_{i-1}) + \alpha\,|V|}

$$

분모의 $\alpha |V|$는 모든 가능한 다음 단어 $|V|$개에 각각 $\alpha$를 더했기 때문에 정규화를 위해 들어간다. $\alpha = 1$ 이면 고전적 **Laplace smoothing**, $0 < \alpha < 1$이면 **Lidstone smoothing**.

**장점**: 구현이 한 줄. 0을 확실히 없앤다.
**단점**: $|V|$가 크면 본 적 있는 n-gram의 확률을 **너무 많이 깎는다**. 결과적으로 perplexity가 의외로 잘 안 줄거나 오히려 악화된다.

### 8.2 Absolute Discounting

본 적 있는 n-gram의 카운트에서 **고정된 양 $d$**를 무조건 빼고, 그렇게 빼앗은 확률 질량을 unseen n-gram들에 다시 분배한다.

$$
\text{Count}^{*}(w_{i-1}, w_i) = C(w_{i-1}, w_i) - d \quad (\text{보통 } d \approx 0.5)

$$

문맥 $w_{i-1}$에서 떼어낸 총 확률 질량은

$$
\alpha(w_{i-1}) = 1 - \sum_{w} \frac{\text{Count}^{*}(w_{i-1}, w)}{C(w_{i-1})}

$$

이다. 강의 예시: $w_{i-1} = \text{the}$, $C(\text{the}) = 48$, 뒤에 등장한 단어 종류 10개 → $\alpha(\text{the}) = 10 \times \frac{0.5}{48} = \frac{5}{48}$.

확률은 카운트 유무에 따라 두 갈래로 정의된다.

$$
P_{\text{abs-disc}}(w_i \mid w_{i-1}) =
\begin{cases}
\dfrac{C(w_{i-1}, w_i) - d}{C(w_{i-1})} & \text{if } C(w_{i-1}, w_i) > 0 \\[8pt]
\alpha(w_{i-1}) \cdot \dfrac{P(w_i)}{\sum_{w'} P(w')} & \text{if } C(w_{i-1}, w_i) = 0
\end{cases}

$$

분배 시 단순 균등 대신 **하위 차수 모델(unigram)**을 가중치로 쓰는 점이 핵심이다.

### 8.3 Linear Interpolation

서로 다른 차수의 n-gram을 **가중 평균** 한다.

$$
\hat{P}(w_i \mid w_{i-2}, w_{i-1}) = \lambda_1 P(w_i \mid w_{i-2}, w_{i-1}) + \lambda_2 P(w_i \mid w_{i-1}) + \lambda_3 P(w_i)

$$

조건 $\sum_i \lambda_i = 1$ 과 $\lambda_i \geq 0$만 지키면 결과가 자동으로 확률이 된다. trigram이 본 적 없는 history라도 bigram·unigram 항이 살아 있어 **0 확률이 사라진다**.

**$\lambda$의 학습**:

1. train set에서 각 차수의 n-gram 확률을 추정
2. **held-out development(validation) set**에서의 perplexity를 최소화하도록 $\lambda$ 를 EM 또는 그리드/그래디언트로 탐색
3. 최종 모델로 test set 평가

실무에서 가장 강건한 단순 smoothing으로 알려져 있다 (Kneser–Ney 같은 더 정교한 변형이 있으나 범위 외).

---

## 핵심 용어 정리


| 한국어             | 영어                             | 기호                 |
| -------------------- | ---------------------------------- | ---------------------- |
| 어휘               | vocabulary                       | $V$                  |
| 코퍼스             | corpus                           | —                   |
| 결합 확률          | joint probability                | $P(w_1, \dots, w_n)$ |
| 조건부 확률        | conditional probability          | $P(w_i \mid \cdot)$  |
| 체인 룰            | chain rule                       | —                   |
| 마르코프 가정      | Markov assumption                | —                   |
| n-그램             | n-gram                           | —                   |
| 최대우도추정       | maximum likelihood estimation    | MLE                  |
| 외재적/내재적 평가 | extrinsic / intrinsic evaluation | —                   |
| 펄플렉시티         | perplexity                       | $\mathrm{ppl}$       |
| 교차 엔트로피      | cross-entropy                    | $H$                  |
| 평활화             | smoothing                        | —                   |
| 가산 평활          | additive (Laplace) smoothing     | $\alpha$             |
| 절대 디스카운팅    | absolute discounting             | $d$                  |
| 보간               | linear interpolation             | $\lambda_i$          |
| 미관찰 단어        | out-of-vocabulary                | OOV                  |
| 그리디 디코딩      | greedy decoding                  | $\arg\max$           |
| 핵 샘플링          | nucleus (top-$p$) sampling       | $p$                  |

---

## 실습 스크립트


| 번호 | 파일                                                             | 내용                                                                                     |
| :----: | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
|  01  | [`code/01_ngram_basics.py`](code/01_ngram_basics.py)             | n-gram 카운트, MLE 추정, 어휘 폭발과 OOV 비율 측정                                       |
|  02  | [`code/02_generation_methods.py`](code/02_generation_methods.py) | bigram/trigram으로 문장 생성, greedy / top-$k$ / top-$p$ 비교                            |
|  03  | [`code/03_perplexity.py`](code/03_perplexity.py)                 | n별 perplexity 측정, train/test 분리, 단조감소 패턴 재현                                 |
|  04  | [`code/04_smoothing.py`](code/04_smoothing.py)                   | unsmoothed (inf) → Laplace($\alpha$ 스윕) → Absolute Discounting → Interpolation 비교 |

---
