import pandas as pd
from sqlalchemy import create_engine
from textblob import TextBlob
import re
import time

# 1. Connect to your SQLite database
engine = create_engine('sqlite:///zomato_pm.db')

print("📥 Pulling raw reviews from database...")
df = pd.read_sql("SELECT * FROM user_reviews", engine)
print(f"Loaded {len(df)} reviews. Starting NLP processing...\n")

# 2. Define the Text Cleaning Function
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    # Remove special characters and URLs, keep basic punctuation
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    text = re.sub(r"[^\w\s.,!?']", '', text)
    return text.strip()

# 3. Define the Sentiment Analysis Function
def get_sentiment(text):
    # TextBlob calculates polarity from -1.0 (highly negative) to 1.0 (highly positive)
    score = TextBlob(text).sentiment.polarity
    
    if score > 0.1:
        category = 'Positive'
    elif score < -0.1:
        category = 'Negative'
    else:
        category = 'Neutral'
        
    return score, category

# 4. Define the Topic Clustering Function
def categorize_topic(text):
    text_lower = text.lower()
    
    # Keyword clusters based on common food delivery complaints
    if any(word in text_lower for word in ['late', 'time', 'delay', 'wait', 'slow', 'tracking']):
        return 'Delivery Speed'
    elif any(word in text_lower for word in ['cold', 'stale', 'taste', 'quality', 'hygiene', 'missing']):
        return 'Food Quality'
    elif any(word in text_lower for word in ['refund', 'money', 'expensive', 'charge', 'price', 'scam']):
        return 'Pricing & Refunds'
    elif any(word in text_lower for word in ['support', 'bot', 'customer service', 'executive', 'call']):
        return 'Customer Support'
    elif any(word in text_lower for word in ['crash', 'glitch', 'update', 'login', 'stuck', 'ui']):
        return 'App & UI Bugs'
    else:
        return 'General/Other'

# 5. Apply the NLP Pipeline
start_time = time.time()
print("🧹 Cleaning text...")
df['clean_text'] = df['review_text'].apply(clean_text)

print("🧠 Analyzing sentiment (this may take 15-30 seconds)...")
# Apply sentiment function and split into two columns
df[['sentiment_score', 'sentiment_category']] = df['clean_text'].apply(
    lambda x: pd.Series(get_sentiment(x))
)

print("🏷️ Clustering topics...")
df['primary_topic'] = df['clean_text'].apply(categorize_topic)

processing_time = round(time.time() - start_time, 1)
print(f"✅ NLP Pipeline completed in {processing_time} seconds.\n")

# 6. Save the processed data back to a NEW SQL table
print("💾 Saving processed insights back to database...")
df.to_sql('processed_reviews', con=engine, if_exists='replace', index=False)

# 7. Print a quick PM Summary
print("\n--- 📊 Quick PM Analytics Preview ---")
print("\nSentiment Breakdown:")
print(df['sentiment_category'].value_counts(normalize=True).mul(100).round(1).astype(str) + '%')

print("\nTop Complaint Categories (Negative Reviews Only):")
neg_df = df[df['sentiment_category'] == 'Negative']
print(neg_df['primary_topic'].value_counts().head(3))