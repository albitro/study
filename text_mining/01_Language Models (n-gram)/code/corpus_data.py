import re
from typing import Any
import numpy as np

_TEMPLATES = [
    # 일상
    "the cat sat on the mat",
    "the dog sat on the floor",
    "the cat ran across the floor",
    "the dog ran across the yard",
    "a cat is sleeping on the chair",
    "a dog is sleeping on the bed",
    "the cat likes to chase the ball",
    "the dog likes to chase the cat",
    "she gave the cat some food",
    "he gave the dog some water",
    "the cat looked at the bird",
    "the dog looked at the man",
    "the man walked into the room",
    "the woman walked into the kitchen",
    "the boy went to the park",
    "the girl went to the school",
    "the children played in the garden",
    "the children played in the park",
    "the man read the newspaper",
    "the woman read the book",
    "the boy ate an apple",
    "the girl ate a sandwich",
    "she opened the door slowly",
    "he opened the window quickly",
    "the door was closed",
    "the window was open",
    "she sat down on the chair",
    "he sat down on the sofa",
    "the kitchen was very clean",
    "the room was very warm",

    # 음식
    "i like to eat chinese food for lunch",
    "i want to eat italian food for dinner",
    "we want to spend the evening together",
    "we like to eat breakfast at home",
    "they want to eat lunch at the restaurant",
    "she likes to drink coffee in the morning",
    "he likes to drink tea in the afternoon",
    "the chef cooked a delicious meal",
    "the waiter brought the menu",
    "the food was very tasty",
    "the soup was hot and salty",
    "the bread was fresh and warm",
    "we ordered pizza for dinner",
    "we ordered pasta for lunch",
    "she made a cake for the party",
    "he made coffee for everyone",
    "the apple is red and sweet",
    "the orange is round and juicy",
    "i bought some bread at the store",
    "i bought some milk at the market",

    # 학교/공부
    "the student wrote a long paper",
    "the teacher read the long paper",
    "the student asked a difficult question",
    "the teacher answered the difficult question",
    "the class started at nine",
    "the lecture ended at noon",
    "she studied math for three hours",
    "he studied history for two hours",
    "the children learned to read",
    "the children learned to write",
    "the book was on the desk",
    "the pen was on the table",
    "the notebook was open on the desk",
    "the homework was very hard",
    "the test was very easy",
    "the exam will be next week",
    "the exam was last week",

    # 일/사무
    "the company released a new product",
    "the company announced a new policy",
    "the manager reviewed the report",
    "the engineer fixed the bug",
    "the engineer built a new system",
    "the team finished the project on time",
    "the team started a new project",
    "she sent the email yesterday",
    "he received the email this morning",
    "the meeting will be on monday",
    "the meeting was on friday",
    "they discussed the plan in detail",
    "we discussed the budget yesterday",
    "the office was very quiet",
    "the office was very busy",

    # 날씨/자연
    "the sun is shining today",
    "the rain is falling outside",
    "the wind is blowing strongly",
    "the snow is falling slowly",
    "the sky is blue and clear",
    "the sky is dark and cloudy",
    "the river is flowing fast",
    "the trees are tall and green",
    "the flowers are red and yellow",
    "the mountain is very high",
    "the lake is very deep",
    "the forest is dark and quiet",
    "birds were singing in the trees",
    "fish were swimming in the river",

    # 여행/이동
    "we went to the city by train",
    "they went to the country by car",
    "the plane took off at noon",
    "the plane landed at midnight",
    "the train arrived on time",
    "the bus arrived late",
    "she took a taxi to the airport",
    "he drove his car to the office",
    "they walked to the park together",
    "we visited the museum yesterday",
    "we visited the castle last summer",
    "the hotel was clean and quiet",
    "the hotel was old but charming",

    # 기술/언어
    "the model predicted the next word",
    "the model generated a long sentence",
    "the algorithm processed the data quickly",
    "the algorithm found the best solution",
    "the program crashed in the middle",
    "the program ran without errors",
    "the language model assigns probabilities to sequences",
    "the language model learns from the corpus",
    "the n gram model uses recent context",
    "the n gram model is simple but effective",
    "the bigram model uses one previous word",
    "the trigram model uses two previous words",
    "the unigram model ignores context completely",
    "the perplexity is a measure of model quality",
    "the smoothing handles unseen sequences",
    "the laplace smoothing adds one to all counts",
    "the absolute discounting subtracts a fixed value",
    "the linear interpolation combines several models",

    # 감정/추상
    "she was very happy yesterday",
    "he was very tired this morning",
    "they were very excited about the trip",
    "we were very sad about the news",
    "she felt nervous before the exam",
    "he felt confident after the interview",
    "the news was good",
    "the news was bad",
    "the story was long and interesting",
    "the story was short but powerful",
    "the movie was very funny",
    "the song was very sad",
]

_EXTRA = [
    "the man who lives next door is very kind",
    "the woman who teaches math is very strict",
    "the cat that we adopted last year is friendly",
    "the dog that we adopted last month is playful",
    "she said that she would come tomorrow",
    "he said that he would call later",
    "they believe that the project will succeed",
    "we believe that the answer is correct",
    "the problem is that we have no time",
    "the problem is that we have no money",
    "the question is how we should proceed",
    "the question is when we should start",
    "i think we should go now",
    "i think we should wait a little",
    "i hope it will not rain tomorrow",
    "i hope you will enjoy the party",
    "if you study hard you will pass the exam",
    "if you work hard you will get the job",
    "when the sun rises the birds start singing",
    "when the rain stops we will go outside",
    "while she was reading he was cooking",
    "while we were eating they were talking",
    "before going to bed she read a book",
    "after finishing dinner he watched a movie",
    "after the meeting we went to lunch",
    "before the meeting we prepared the slides",
    "the more you read the more you learn",
    "the more you practice the better you become",
    "the harder you work the more you achieve",
    "she is taller than her brother",
    "he is younger than his sister",
    "this book is more interesting than that one",
    "this exam is easier than the last one",
    "today is colder than yesterday",
    "today is warmer than yesterday",
]

_REPEATED = [
    "the cat sat on the mat",
    "the dog ran across the yard",
    "i like to eat",
    "we want to go",
    "she said that she would come",
    "the model is very good",
    "the company released a new product",
    "the meeting was on friday",
    "the sun is shining",
    "the rain is falling",
] * 3


def get_corpus(seed: int = 0, repeats: int = 3) -> list[list[str]]:
    rng = np.random.default_rng(seed)
    sents = (_TEMPLATES * repeats) + _EXTRA + _REPEATED
    sents = sents.copy()
    rng.shuffle(sents)

    out: list[list[str]] = []
    for s in sents:
        toks = re.findall(r"[a-z]+", s.lower())
        if not toks:
            continue
        out.append(["<s>"] + toks + ["</s>"])
    return out


def split_corpus(
    seed: int = 0,
    train_ratio: float = 0.8,
    repeats: int = 3,
) -> tuple[list[list[str]], list[list[str]]]:
    sents = get_corpus(seed=seed, repeats=repeats)
    rng = np.random.default_rng(seed + 1)
    idx = np.arange(len(sents))
    rng.shuffle(idx)
    n_train = int(len(sents) * train_ratio)
    train = [sents[i] for i in idx[:n_train]]
    test = [sents[i] for i in idx[n_train:]]
    return train, test


def vocabulary(sents: list[list[str]]) -> list[str]:
    vocab = set[Any]()
    for s in sents:
        vocab.update(s)
    return sorted(vocab)


if __name__ == "__main__":
    corpus = get_corpus()
    vocab = vocabulary(corpus)
    n_tokens = sum(len(s) for s in corpus)
    print(f"# sentences : {len(corpus)}")
    print(f"# tokens    : {n_tokens}")
    print(f"# vocab     : {len(vocab)}")
    print(f"sample      : {' '.join(corpus[0])}")