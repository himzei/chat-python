from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# 모델 로드 (최초 1회만 다운로드)
tokenizer = AutoTokenizer.from_pretrained("beomi/kcbert-base")
model = AutoModelForSequenceClassification.from_pretrained("beomi/kcbert-base", num_labels=2)

def analyze_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)
    
    # 0: 부정, 1: 긍정
    sentiment_score = probs[0][1].item()  # 긍정 확률
    polarity = (sentiment_score - 0.5) * 2  # -1 ~ 1로 변환
    
    return {
        'polarity': polarity,
        'positive_prob': sentiment_score,
        'negative_prob': probs[0][0].item()
    }

# 사용 예시
text = "오늘 정말 기분이 좋아요! 날씨도 화창하고 모든 일이 잘 풀렸어요."
result = analyze_sentiment(text)

print(f"극성(Polarity): {result['polarity']:.3f}")  # -1(부정) ~ 1(긍정)
print(f"긍정 확률: {result['positive_prob']:.3f}")
print(f"부정 확률: {result['negative_prob']:.3f}")