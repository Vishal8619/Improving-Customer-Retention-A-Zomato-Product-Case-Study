import os
import pandas as pd
from google_play_scraper import Sort, reviews
from datetime import datetime

def scrape_test_batch(app_id='com.application.zomato', target_count=1000):
    """
    Scrapes a specific number of reviews for a given app ID 
    and handles token pagination automatically.
    """
    all_reviews = []
    continuation_token = None
    extracted_count = 0
    
    print(f"🚀 Initializing scraper for App ID: {app_id}")
    print(f"🎯 Target count set to: {target_count} reviews\n")
    
    while extracted_count < target_count:
        # Calculate how many reviews to fetch in this batch (Max 200 per API call)
        remaining = target_count - extracted_count
        batch_size = min(remaining, 200)
        
        # Fetch data from Google Play Store API
        batch, continuation_token = reviews(
            app_id,
            lang='en',       # Extract English/Hinglish reviews
            country='in',    # Target the Indian market
            sort=Sort.NEWEST, # Get the latest feedback
            count=batch_size,
            continuation_token=continuation_token
        )
        
        if not batch:
            print("⚠️ No more reviews returned. Breaking loop.")
            break
            
        all_reviews.extend(batch)
        extracted_count = len(all_reviews)
        print(f"📥 Pulled batch: {len(batch)} reviews | Total collected: {extracted_count}/{target_count}")
        
        # Break if there's no further page to look at
        if not continuation_token:
            print("🏁 Reached the end of available pagination tokens.")
            break
            
    # Process into a structured DataFrame
    print("\nTransforming raw JSON into structured format...")
    df = pd.DataFrame(all_reviews)
    
    # Extract only fields critical for PM / Sentiment / Version analysis
    keep_columns = {
        'reviewId': 'review_id',
        'userName': 'user_name',
        'score': 'rating',
        'thumbsUpCount': 'thumbs_up_count',
        'reviewCreatedVersion': 'app_version',
        'at': 'created_at',
        'content': 'review_text'
    }
    
    df = df[list(keep_columns.keys())].rename(columns=keep_columns)
    
    # Handle missing values in app version
    df['app_version'] = df['app_version'].fillna('Unknown')
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    return df

if __name__ == "__main__":
    # Execute the scrape for 5000 reviews
    data = scrape_test_batch(app_id='com.application.zomato', target_count=5000)
    
    # Save to a new CSV file
    output_filename = "zomato_reviews_5k.csv"
    data.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Success! Scraped {len(data)} rows.")
    print(f"📁 File saved locally as: {os.path.abspath(output_filename)}")