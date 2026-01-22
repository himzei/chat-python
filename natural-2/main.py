from textblob import TextBlob

text = "I love this product! It's amazing and wonderful."

blob = TextBlob(text)
sentiment = blob.sentiment

print(f"극성(Polarity): {sentiment.polarity}")  # -1(부정) ~ 1(긍정)
print(f"주관성(Subjectivity): {sentiment.subjectivity}")  # 0(객관) ~ 1(주관)