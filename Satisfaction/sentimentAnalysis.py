import pandas as pd
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax
import re
import torch

def preprocess(text):
    if not isinstance(text, str):
        return "" 
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\S+", "", text)
    text = re.sub(r"#\S+", "", text)
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text

MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)

# Determine device and move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = AutoModelForSequenceClassification.from_pretrained(MODEL).to(device)

if torch.cuda.is_available():
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")
else:
    print("Using CPU")

import torch
import numpy as np

def analyze_sentiment(df):
    sentiments = []
    textCount = 0
    model.eval()  # Set model to evaluation mode

    for text in df["Message"]:
        try:
            print(textCount)
            text = preprocess(text)
            # Tokenize and move inputs to the same device as the model
            encoded_input = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512).to(device)  # Add padding, truncation, and max_length
            with torch.no_grad():  # Disable gradient calculation
                output = model(**encoded_input)

            # Move logits to CPU and process
            scores = output.logits[0].cpu().numpy() # Access logits correctly
            scores = softmax(scores)
            ranking = np.argsort(scores)[::-1]
            sentiment_label = config.id2label[ranking[0]]
            sentiment_score = scores[ranking[0]]
            sentiments.append({"label": sentiment_label, "score": float(sentiment_score)}) #convert score to float for json serialization

        except Exception as e:
            print(f"Error processing message: {text}")
            print(f"Error: {e}")
            sentiments.append({"label": "ERROR", "score": 0.0})
        finally:
            # Explicitly delete tensors to free GPU memory, even if errors occur.
            if 'encoded_input' in locals():
                del encoded_input
            if 'output' in locals():
                del output
            torch.cuda.empty_cache() # Empty cache after each iteration

        textCount += 1

    return sentiments

df = pd.read_csv("test.csv")
sentiment_results = analyze_sentiment(df)
df["Sentiment"] = [result["label"] for result in sentiment_results]
df.to_csv("updated_test.csv", index=False)
print("Sentiment analysis complete. Results saved to updated_test.csv")