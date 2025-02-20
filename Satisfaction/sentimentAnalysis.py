import pandas as pd
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax
import re

def preprocess(text):
    if not isinstance(text, str):  # Handle non-string inputs
        return "" 

    text = re.sub(r"http\S+", "", text)  # Remove URLs
    text = re.sub(r"@\S+", "", text)  # Remove mentions
    text = re.sub(r"#\S+", "", text)  # Remove hashtags
    text = text.lower()  # Lowercase
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra whitespace
    return text

MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

def analyze_sentiment(df):
    sentiments = []
    for text in df["Message"]:
        try:
            text = preprocess(text)
            encoded_input = tokenizer(text, return_tensors='pt')
            output = model(**encoded_input)
            scores = output[0][0].detach().numpy()
            scores = softmax(scores)

            ranking = np.argsort(scores)
            ranking = ranking[::-1]

            sentiment_label = config.id2label[ranking[0]]
            sentiment_score = scores[ranking[0]]

            sentiments.append({"label": sentiment_label, "score": sentiment_score})

        except Exception as e:
            print(f"Error processing message: {text}")
            print(f"Error: {e}")
            sentiments.append({"label": "ERROR", "score": 0.0})

    return sentiments

df = pd.read_csv("test.csv")
sentiment_results = analyze_sentiment(df)
df["Sentiment"] = [result["label"] for result in sentiment_results]

# Commented out the score just in case we need it later
#df["Sentiment_Score"] = [result["score"] for result in sentiment_results] 

df.to_csv("updated_test.csv", index=False)
print("Sentiment analysis complete. Results saved to updated_test.csv")