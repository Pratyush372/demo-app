import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 Demo Data Explorer")

# File uploader
file = st.file_uploader("Upload a CSV file", type=["csv"])

if file:
    df = pd.read_csv(file)
    st.subheader("Data Preview")
    st.dataframe(df.head())

    # Choose column for visualization
    column = st.selectbox("Pick a numeric column to plot", df.select_dtypes(include="number").columns)

    if column:
        fig, ax = plt.subplots()
        ax.hist(df[column].dropna(), bins=20)
        ax.set_title(f"Distribution of {column}")
        st.pyplot(fig)
