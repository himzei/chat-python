from wordcloud import WordCloud
import matplotlib.pyplot as plt 
from collections import Counter 

text = """
인공지능 발전과 신뢰 기반 조성 등에 관한 기본법(AI기본법)이 이날부터 전면 시행에 들어갔다. AI 관련 부분 규제가 아닌 포괄적 법령으로는 세계 최초 시행이다. 유럽연합(EU)이 2024년 AI법을 통과시켰지만 고위험 AI 규제 적용 시점을 단계적으로 늦춘 상황을 고려하면, 실제로 전면 적용하는 국가는 한국이 가장 이른 사례가 될 가능성이 크다.
정부는 딥페이크, 허위 사실 유포, 인권 침해 등 고도화된 AI의 폐해로부터 사회를 지킬 규범이 필요하다며 업계 우려를 고려해 정부의 사실 조사권이나 과태료 부과를 1년 이상 유예하는 등 '연착륙'을 시도하겠다는 입장이다.
AI기본법은 AI의 건전한 활용을 위해 국가가 AI 업계를 지원하는 한편 폐해가 예상되는 위험한 AI의 활용은 예방하는 데 방점을 뒀다. 진흥책으로 과학기술정보통신부 장관이 3년마다 AI와 관련 산업의 진흥, 국가 경쟁력 강화를 위해 AI기본계획을 세워 시행하도록 했다. 국가인공지능전략위원회는 법정 위원회로 승격됐다.
국가와 지방자치단체가 AI 사업자의 창의 정신을 존중하며 관련 제품·서비스의 연구개발을 지원하도록 했다. 규제책으로 정부는 AI가 국민 생활에 미치는 잠재적 위험을 최소화하고 안전한 이용을 위한 제도를 정비하도록 했다. AI 안전성·신뢰성 확보를 위한 기술 개발, 교육, 홍보를 지원해야 한다.
AI기본법은 AI 기술·산업 등과 관련해 다른 법률에 특별한 규정이 있는 경우를 제외하고는 이 법에서 정하는 바에 따른다며 AI에 관한 포괄적이고 상위적인 지위를 가짐을 명시하고 있다. AI 등 디지털 서비스에 적용할 수 있는 대표적 기존 법규인 전기통신사업법과 정보통신망법이 AI 발전을 따라가지 못하며 규제 공백이 있다는 문제의식이 AI기본법을 낳았다.
"""

wordcloud = WordCloud(
    width=800, 
    height=300, 
    background_color='white',
    colormap="plasma",
    font_path='C:/Windows/Fonts/malgun.ttf',  # 한글 폰트 경로 지정 (맑은 고딕)
    max_words=100,  # 최대 단어 개수
    relative_scaling=0.5  # 단어 크기 비율 조정
).generate(text)

plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.title("테스트 워드클라우드", fontproperties='Malgun Gothic')
plt.show()
