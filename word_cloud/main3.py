from textblob import TextBlob

text = 'Donald Trump says "things are really calming down" as he joins other world leaders at a signing ceremony for his Board of Peace"'


blob = TextBlob(text)
sentiment = blob.sentiment 

print(f"극성(Polarity): {sentiment.polarity}")  # -1(부정) ~ 1(긍정)
print(f"주관성(Subjectivity): {sentiment.subjectivity}")  # 0(