import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# 1. Page Configuration (Wide & Dark Mode Optimized)
st.set_page_config(page_title="Zomato PM Dashboard", page_icon="🌶️", layout="wide")

# 2. Custom CSS for "Crazy/Vibrant" Look
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #e23744 0%, #ff5e69 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(226, 55, 68, 0.4);
        margin-bottom: 20px;
    }
    .metric-title { font-size: 1.2rem; font-weight: 600; opacity: 0.9; }
    .metric-value { font-size: 2.5rem; font-weight: 800; margin: 10px 0; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

st.title("🌶️ Zomato Product Intelligence Engine")
st.markdown("Live sentiment tracking and feature analytics based on user reviews.")

# 3. Load Data from SQLite
@st.cache_data
def load_data():
    engine = create_engine('sqlite:///zomato_pm.db')
    df = pd.read_sql("SELECT * FROM processed_reviews", engine)
    df['created_at'] = pd.to_datetime(df['created_at'])
    return df

try:
    df = load_data()
except Exception as e:
    st.error("⚠️ Could not load database. Make sure zomato_pm.db exists.")
    st.stop()

# 4. Vibrant High-Level Metrics Row using Custom HTML
total_reviews = len(df)
positive_pct = round((len(df[df['sentiment_category'] == 'Positive']) / total_reviews) * 100, 1)
negative_pct = round((len(df[df['sentiment_category'] == 'Negative']) / total_reviews) * 100, 1)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Reviews Analyzed</div><div class="metric-value">{total_reviews:,}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);"><div class="metric-title">Positive Sentiment</div><div class="metric-value">{positive_pct}%</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card" style="background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);"><div class="metric-title">Critical Churn Risk</div><div class="metric-value">{negative_pct}%</div></div>', unsafe_allow_html=True)

st.divider()

# 5. The "Crazy" Sunburst Chart & Advanced Visuals
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.markdown("#### 🌀 The Sentiment Matrix (Interactive)")
    # Prepare data for Sunburst (Filtering out 'General/Other' for cleaner rings)
    sunburst_df = df[df['primary_topic'] != 'General/Other']
    
    fig_sunburst = px.sunburst(
        sunburst_df, 
        path=['sentiment_category', 'primary_topic'], 
        color='sentiment_category',
        color_discrete_map={'Positive':'#00b09b', 'Neutral':'#fbc531', 'Negative':'#e84118'},
        height=500
    )
    fig_sunburst.update_traces(textinfo="label+percent parent")
    fig_sunburst.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_sunburst, width='stretch')

with col_right:
    st.markdown("#### 🔥 Top Friction Points")
    neg_df = df[df['sentiment_category'] == 'Negative']
    topic_counts = neg_df['primary_topic'].value_counts().reset_index()
    topic_counts.columns = ['Topic', 'Count']
    topic_counts = topic_counts[topic_counts['Topic'] != 'General/Other']
    
    fig_bar = px.bar(
        topic_counts, 
        x='Count', 
        y='Topic', 
        orientation='h',
        color='Count',
        color_continuous_scale='Inferno', # High contrast vibrant colors
        height=500
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_bar, width='stretch')

st.divider()

# 6. The PM "Drill-Down" Table
st.markdown("### 🔍 Raw Intelligence Drill-Down")
worst_topic = topic_counts['Topic'].iloc[0] if not topic_counts.empty else "Delivery Speed"

st.caption(f"Showing recent critical reviews for: **{worst_topic}**")
drill_down_df = neg_df[neg_df['primary_topic'] == worst_topic][['created_at', 'rating', 'app_version', 'review_text']].head(10)

st.dataframe(
    drill_down_df,
    column_config={
        "created_at": "Date",
        "rating": st.column_config.NumberColumn("Rating", format="⭐ %d"),
        "app_version": "App Version",
        "review_text": "User Feedback"
    },
    hide_index=True,
    width='stretch'
)