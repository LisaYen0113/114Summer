from transformers import pipeline

# 載入中文情感分析模型 (HuggingFace 已經訓練好的)
classifier = pipeline("sentiment-analysis", model="uer/roberta-base-finetuned-jd-binary-chinese")

def analyze_sentiment(text):
    result = classifier(text)[0]
    label = result['label']
    score = result['score']
    
    if label == "positive":
        return f"情感：正向 (信心 {score:.2f})"
    elif label == "negative":
        return f"情感：負向 (信心 {score:.2f})"
    else:
        return f"情感：中立 (信心 {score:.2f})"

# 測試
print(analyze_sentiment("板橋晚上不安全"))
print(analyze_sentiment("這裡環境很乾淨"))
print(analyze_sentiment("還可以啦沒什麼特別"))
