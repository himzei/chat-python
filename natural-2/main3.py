from collections import Counter

text = "파이썬은 쉽다 파이썬은 강력하다 파이썬으로 개발하자"
words = text.split()

# 단어 빈도 계산
word_freq = Counter(words)
print("단어 빈도:", word_freq)
print("가장 많이 나온 단어:", word_freq.most_common(2))