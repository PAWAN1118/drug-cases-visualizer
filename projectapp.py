import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px

# Load the JSON data from the provided URL
url = "https://www.data.gov.in/backend/dms/v1/ogdp/resource/download/603189971/json/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJkYXRhLmdvdi5pbiIsImF1ZCI6ImRhdGEuZ292LmluIiwiaWF0IjoxNzQxMTYxNzE3LCJleHAiOjE3NDExNjIwMTcsImRhdGEiOnsibmlkIjoiNjAzMTg5OTcxIn19.0G6wbxOJRrimBOB-OQmMx1rP8TcHXEZqgGGiGzBynqI"

@st.cache_data
def load_data():
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            if "fields" in data and "data" in data:
                columns = [field["label"] for field in data["fields"]]
                df = pd.DataFrame(data["data"], columns=columns)
                return df
            else:
                st.error("Unexpected JSON structure. Please check the API response.")
                return pd.DataFrame()
        except ValueError:
            st.error("Error: Failed to parse JSON response.")
            return pd.DataFrame()
    else:
        st.error(f"Error: Failed to fetch data from the URL. Status code: {response.status_code}")
        return pd.DataFrame()

# Load Data
df = load_data()

# Reshape Data
def preprocess_data(df):
    df_melted = df.melt(id_vars=["Sl. No.", "State/UT"], var_name="Year_DrugType", value_name="Seizure Quantity")
    df_melted[['Year', 'Drug Type']] = df_melted['Year_DrugType'].str.extract(r'(\\d{4}) - (.+)')
    df_melted.drop(columns=['Year_DrugType'], inplace=True)
    df_melted.dropna(inplace=True)
    df_melted['Year'] = df_melted['Year'].astype(int)
    df_melted['Seizure Quantity'] = pd.to_numeric(df_melted['Seizure Quantity'], errors='coerce')
    df_melted.dropna(inplace=True)
    return df_melted

processed_data = preprocess_data(df)

# UI Layout
st.set_page_config(page_title="NDPS Seizure Analysis", layout="wide")

# Sidebar Filters
st.sidebar.title("Filters")
year_input = st.sidebar.selectbox("Select Year", sorted(processed_data["Year"].unique(), reverse=True))
drug_type_filter = st.sidebar.multiselect("Select Drug Type", processed_data["Drug Type"].unique(), default=processed_data["Drug Type"].unique())

# Filter Data
filtered_df = processed_data[(processed_data['Year'] == year_input) & (processed_data['Drug Type'].isin(drug_type_filter))]

# Dashboard Title
st.title("📊 NDPS Seizure Analysis Dashboard")
st.markdown("Analyze drug seizure trends across India from 2018 to 2022.")

# Key Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="📌 Total Seizures", value=int(filtered_df["Seizure Quantity"].sum()))
with col2:
    most_seized_drug = filtered_df.groupby("Drug Type")["Seizure Quantity"].sum().idxmax()
    st.metric(label="🚀 Most Seized Drug", value=most_seized_drug)
with col3:
    top_state = filtered_df.groupby("State/UT")["Seizure Quantity"].sum().idxmax()
    st.metric(label="📍 State with Highest Cases", value=top_state)

# Data Table
st.subheader(f"Seizure Data for {year_input}")
st.dataframe(filtered_df)

# Visualization: Bar Chart
st.subheader("🔍 Seizure Quantity by Drug Type")
fig_bar = px.bar(filtered_df.groupby("Drug Type")["Seizure Quantity"].sum().reset_index(), 
                 x="Drug Type", 
                 y="Seizure Quantity", 
                 color="Drug Type", 
                 title=f"Drug Seizures in {year_input}")
st.plotly_chart(fig_bar, use_container_width=True)

# Visualization: Line Chart
st.subheader("📈 Monthly Seizure Trends")
fig_line = px.line(filtered_df.groupby("Year")["Seizure Quantity"].sum().reset_index(), 
                    x="Year", 
                    y="Seizure Quantity", 
                    markers=True, 
                    title=f"Yearly Seizure Trends")
st.plotly_chart(fig_line, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Made with ❤️ by AI Student")
