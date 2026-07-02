import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="AI Models Performance Analytics",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------
# Dashboard Title
# -------------------------------
st.title("🤖 AI Models Performance Analytics Dashboard")

st.markdown("""
Welcome to the AI Models Performance Analytics Dashboard.

This dashboard provides exploratory data analysis and insights into:
- Model Intelligence vs. Pricing Efficiency
- Generation Speed and Latency Trends
- Creator/Company Benchmarks
- Top Performing & Most Cost-Effective Models
""")

# -------------------------------
# Load & Clean Dataset
# -------------------------------
@st.cache_data
def load_data():
    # Load dataset
    df = pd.read_csv("Data/ai_models_performance.csv")
    
    # Drop duplicates if any
    df = df.drop_duplicates()

    # Convert numeric columns safely
    df["Intelligence Index"] = pd.to_numeric(
        df["Intelligence Index"],
        errors="coerce"
    )

    # Clean and convert Price column
    df["Price (Blended USD/1M Tokens)"] = (
        df["Price (Blended USD/1M Tokens)"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    df["Price (Blended USD/1M Tokens)"] = pd.to_numeric(
        df["Price (Blended USD/1M Tokens)"],
        errors="coerce"
    )

    df["Speed(median token/s)"] = pd.to_numeric(
        df["Speed(median token/s)"],
        errors="coerce"
    )

    df["Latency (First Answer Chunk /s)"] = pd.to_numeric(
        df["Latency (First Answer Chunk /s)"],
        errors="coerce"
    )

    # Feature Engineering from your notebook
    df['Price Efficiency'] = df['Intelligence Index'] / df['Price (Blended USD/1M Tokens)']
    df['Speed Per Dollar'] = df['Speed(median token/s)'] / df['Price (Blended USD/1M Tokens)']

    return df

df = load_data()

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.title("🔍 Filters")

# Creator Filter
all_creators = sorted(df["Creator"].dropna().unique().tolist())
creator_select = st.sidebar.multiselect(
    "Select Creator",
    options=all_creators,
    default=all_creators
)

# Dynamically filter model options based on selected creators
filtered_models_options = sorted(df[df["Creator"].isin(creator_select)]["Model"].dropna().unique().tolist())

# Model Filter
model_select = st.sidebar.multiselect(
    "Select Model",
    options=filtered_models_options,
    default=filtered_models_options
)

# Apply Filters to Data
filtered_df = df[
    (df["Creator"].isin(creator_select)) & 
    (df["Model"].isin(model_select))
]

# Display filtered record count in sidebar
st.sidebar.write(f"Filtered Records: {len(filtered_df):,}")

# -------------------------------
# KPI Calculations
# -------------------------------
total_models = filtered_df["Model"].nunique()
total_creators = filtered_df["Creator"].nunique()
avg_intelligence = filtered_df["Intelligence Index"].mean()
avg_price = filtered_df["Price (Blended USD/1M Tokens)"].mean()
avg_speed = filtered_df["Speed(median token/s)"].mean()
avg_latency = filtered_df["Latency (First Answer Chunk /s)"].mean()

# Safely extract extremes handling potential empty/NaN states
max_intel_row = filtered_df.loc[filtered_df["Intelligence Index"].idxmax()] if not filtered_df["Intelligence Index"].dropna().empty else None
min_price_row = filtered_df.loc[filtered_df["Price (Blended USD/1M Tokens)"].idxmin()] if not filtered_df["Price (Blended USD/1M Tokens)"].dropna().empty else None
max_speed_row = filtered_df.loc[filtered_df["Speed(median token/s)"].idxmax()] if not filtered_df["Speed(median token/s)"].dropna().empty else None

# -------------------------------
# KPI Section
# -------------------------------
st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Models", f"{total_models}")
with col2:
    st.metric("Unique Creators", f"{total_creators}")
with col3:
    st.metric("Avg Intelligence Index", f"{avg_intelligence:.2f}" if not np.isnan(avg_intelligence) else "N/A")
with col4:
    st.metric("Avg Price (per 1M tokens)", f"${avg_price:.2f}" if not np.isnan(avg_price) else "N/A")

col5, col6, col7, col8 = st.columns(4)
with col5:
    st.metric("Avg Speed", f"{avg_speed:.1f} tok/s" if not np.isnan(avg_speed) else "N/A")
with col6:
    st.metric("Avg Latency", f"{avg_latency:.2f} s" if not np.isnan(avg_latency) else "N/A")
with col7:
    st.metric("Highest Intelligence", f"{max_intel_row['Intelligence Index']:.0f}" if max_intel_row is not None else "N/A", 
              help=f"Model: {max_intel_row['Model']}" if max_intel_row is not None else "")
with col8:
    st.metric("Lowest Price", f"${min_price_row['Price (Blended USD/1M Tokens)']:.2f}" if min_price_row is not None else "N/A", 
              help=f"Model: {min_price_row['Model']}" if min_price_row is not None else "")

st.divider()

# -------------------------------
# Distribution Analysis (Side-by-Side Line/Hist Charts)
# -------------------------------
st.subheader("📊 Distribution Analysis")

left, right = st.columns(2)

with left:
    fig_intel = px.histogram(
        filtered_df,
        x="Intelligence Index",
        nbins=20,
        title="Distribution of Intelligence Index",
        color_discrete_sequence=['#4361ee']
    )
    fig_intel.update_layout(template="plotly_dark", xaxis_title="Intelligence Index", yaxis_title="Count")
    st.plotly_chart(fig_intel, use_container_width=True)

with right:
    fig_price = px.histogram(
        filtered_df,
        x="Price (Blended USD/1M Tokens)",
        nbins=20,
        title="Distribution of Price (USD per 1M Tokens)",
        color_discrete_sequence=['#7209b7']
    )
    fig_price.update_layout(template="plotly_dark", xaxis_title="Price (USD/1M Tokens)", yaxis_title="Count")
    st.plotly_chart(fig_price, use_container_width=True)

# -------------------------------
# Top Performing Models Benchmarks
# -------------------------------
st.subheader("🏆 Top Model Benchmarks")

left, right = st.columns(2)

with left:
    top10_intel = filtered_df.nlargest(10, "Intelligence Index")
    fig_top_intel = px.bar(
        top10_intel,
        x="Intelligence Index",
        y="Model",
        orientation='h',
        color="Creator",
        title="Top 10 Smartest Models"
    )
    fig_top_intel.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top_intel, use_container_width=True)

with right:
    top10_speed = filtered_df.nlargest(10, "Speed(median token/s)")
    fig_top_speed = px.bar(
        top10_speed,
        x="Speed(median token/s)",
        y="Model",
        orientation='h',
        color="Creator",
        title="Top 10 Fastest Models (Median token/s)"
    )
    fig_top_speed.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'}, xaxis_title="Tokens per Second")
    st.plotly_chart(fig_top_speed, use_container_width=True)

st.divider()

# -------------------------------
# Relationship & Efficiency Analysis
# -------------------------------
st.subheader("📈 Relationship Analysis")

left, right = st.columns(2)

with left:
    fig_scatter1 = px.scatter(
        filtered_df,
        x="Price (Blended USD/1M Tokens)",
        y="Intelligence Index",
        color="Creator",
        hover_name="Model",
        title="Price vs. Intelligence"
    )
    fig_scatter1.update_layout(template="plotly_dark")
    st.plotly_chart(fig_scatter1, use_container_width=True)

with right:
    fig_scatter2 = px.scatter(
        filtered_df,
        x="Speed(median token/s)",
        y="Latency (First Answer Chunk /s)",
        color="Creator",
        hover_name="Model",
        title="Generation Speed vs. Initial Latency"
    )
    fig_scatter2.update_layout(template="plotly_dark")
    st.plotly_chart(fig_scatter2, use_container_width=True)

st.divider()

# -------------------------------
# Correlation Heatmap
# -------------------------------
st.subheader("🔥 Metric Correlations")

numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
# Clean list to use core metrics
core_numeric = [c for c in numeric_cols if c not in ['Price Efficiency', 'Speed Per Dollar']]

if len(filtered_df) > 1 and len(core_numeric) > 1:
    fig_heatmap, ax = plt.subplots(figsize=(8, 4))
    fig_heatmap.patch.set_facecolor('#0E1117')  # Match streamlit dark mode background
    ax.set_facecolor('#0E1117')
    
    sns.heatmap(
        filtered_df[core_numeric].corr(),
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        linewidths=0.5,
        ax=ax,
        cbar_kws={"shrink": .8}
    )
    plt.xticks(rotation=45, ha='right', color='white')
    plt.yticks(color='white')
    ax.tick_params(colors='white')
    
    st.pyplot(fig_heatmap)
else:
    st.info("Not enough variations in the selected filters to generate a correlation map.")

st.divider()

# -------------------------------
# Executive Insights
# -------------------------------
st.subheader("💡 Executive Insights")

if max_intel_row is not None and max_speed_row is not None and min_price_row is not None:
    st.success(f"""
    ### Key Findings
    
    • 🧠 **Peak Capability**: The most intelligent model currently selected is **{max_intel_row['Model']}** by *{max_intel_row['Creator']}*, scoring an intelligence index of **{max_intel_row['Intelligence Index']:.0f}**.
    
    • ⚡ **Top Tier Throughput**: **{max_speed_row['Model']}** (*{max_speed_row['Creator']}*) handles maximum generation speeds reaching **{max_speed_row['Speed(median token/s)']:.0f} tokens/second**.
    
    • 💰 **Budget Optimizer**: **{min_price_row['Model']}** by *{min_price_row['Creator']}* offers the minimum blended access entry price point sitting at **${min_price_row['Price (Blended USD/1M Tokens)']:.4f}** per million tokens.
    
    ### Strategic Recommendations
    
    - **High-Complexity Operations**: Deploy flagship variants like `{max_intel_row['Model']}` for reasoning-heavy chains where semantic correctness is vital.
    - **Real-time Interface Apps**: Prioritize low-latency architectures with processing throughputs exceeding `{avg_speed:.0f} tok/s` to maintain responsive streaming UI states.
    - **Cost-Efficiency Architecture**: Mix structured queries by routing secondary classifications to economy options matching `{min_price_row['Model']}` frameworks to scale volume affordably.
    """)

st.divider()

# -------------------------------
# Dataset Overview & Export
# -------------------------------
st.header("Dataset Overview")

col_r, col_c = st.columns(2)
with col_r:
    st.metric("Total Row Rows Evaluated", filtered_df.shape[0])
with col_c:
    st.metric("Feature Properties Evaluated", filtered_df.shape[1])

with st.expander("📂 View Filtered Dataset Preview"):
    st.dataframe(
        filtered_df,
        use_container_width=True
    )

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

col_btn, _ = st.columns([1, 4])
with col_btn:
    st.download_button(
        label="📥 Download Filtered CSV",
        data=csv_data,
        file_name="filtered_ai_models_metrics.csv",
        mime="text/csv"
    )

st.divider()

st.caption(
    "AI Models Performance Analytics Dashboard | Built with Streamlit, Plotly & Pandas | © 2026"
)