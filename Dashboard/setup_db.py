import pandas as pd
from sqlalchemy import create_engine, text

# 1. Create a local SQLite database file in your Zomato folder
engine = create_engine('sqlite:///zomato_pm.db')

print("🏗️ Building SQL Database Schema...")

# 2. Create the tables using raw SQL
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS apps (
            app_id VARCHAR(100) PRIMARY KEY,
            app_name VARCHAR(50) NOT NULL
        );
    """))
    
    conn.execute(text("""
        INSERT OR IGNORE INTO apps (app_id, app_name) VALUES 
        ('com.application.zomato', 'Zomato'),
        ('in.swiggy.android', 'Swiggy');
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS user_reviews (
            review_id VARCHAR(255) PRIMARY KEY,
            app_id VARCHAR(100),
            user_name VARCHAR(255),
            rating INTEGER,
            thumbs_up_count INTEGER,
            app_version VARCHAR(50),
            created_at DATETIME,
            review_text TEXT,
            sentiment_score NUMERIC,
            sentiment_category VARCHAR(10),
            primary_topic VARCHAR(50),
            FOREIGN KEY (app_id) REFERENCES apps(app_id)
        );
    """))
    conn.commit()

# 3. Load the CSV we just scraped
print("📥 Loading CSV data...")
df = pd.read_csv('zomato_reviews_test_5k.csv')

# 4. Add the app_id so we know these are Zomato reviews
df['app_id'] = 'com.application.zomato'

# 5. Push the DataFrame directly into the SQL table
print("🚀 Pushing data to SQL...")
df.to_sql('user_reviews', con=engine, if_exists='append', index=False)

# 6. Run a quick SQL query to verify it worked
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM user_reviews")).scalar()
    print(f"✅ Success! There are now {result} rows in the SQL database.")