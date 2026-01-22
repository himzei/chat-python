from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# 한국어 텍스트
korean_text = """
South Korea’s benchmark stock index Kospi surged past the 5,000-point mark for the first time during trading Thursday, raising expectations that the long-standing “Korea discount” — a term referring to the relatively low valuation of domestic stocks — may finally be fading
"""

# 한국어 워드클라우드 (폰트 경로 지정 필요)
wordcloud = WordCloud(
    font_path='C:/Windows/Fonts/malgun.ttf',  # Windows
    # font_path='/System/Library/Fonts/AppleGothic.ttf',  # Mac
    # font_path='/usr/share/fonts/truetype/nanum/NanumGothic.ttf',  # Linux
    width=300,
    height=300,
    background_color='white',
    colormap='plasma'
).generate(korean_text)

plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('한국어 워드클라우드', fontproperties='Malgun Gothic')
plt.show()