import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =======================
# 🎨 Custom CSS Styling
# =======================
st.markdown(
    """
    <style>
    /* App background */
    .stApp {
        background-color: black;
    }

    /* Title */
    h1 {
        color: #2c3e50;
        text-align: center;
        font-family: 'Segoe UI', sans-serif;
        font-size: 40px;
    }

    /* Subheaders */
    h2, h3 {
        color: #34495e;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Buttons */
    div.stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        background-color: #45a049;
        color: #f5f5f5;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #2c3e50;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] p {
        color: white;
    }

    /* Dataframe Styling */
    .dataframe {
        border: 2px solid #2c3e50;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =======================
# 📊 App Logic
# =======================
st.title("📊 Demo Data Explorer")

# File uploader
file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if file:
    df = pd.read_csv(file)
    st.subheader("🔎 Data Preview")
    st.dataframe(df.head(100))

    # Choose column for visualization
    column = st.selectbox("📈 Pick a numeric column to plot", df.select_dtypes(include="number").columns)

    if column:
        fig, ax = plt.subplots()
        ax.hist(df[column].dropna(), bins=20, color="#4CAF50", edgecolor="black")
        ax.set_title(f"Distribution of {column}", fontsize=14)
        ax.set_xlabel(column)
        ax.set_ylabel("Frequency")
        st.pyplot(fig)
