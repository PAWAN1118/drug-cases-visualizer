import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

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

st.set_page_config(page_title="NDPS Seizure Analysis", layout="wide")
st.title("NDPS Seizure Analysis Dashboard")
st.markdown("This dashboard provides insights into drug seizure data across different states and years.")

# Load and display data
df = load_data()

if not df.empty:
    year_input = st.selectbox("Select Year", options=[2018, 2019, 2020, 2021, 2022])
    df_melted = df.melt(id_vars=["Sl. No.", "State/UT"], var_name="Year_DrugType", value_name="Seizure Quantity")
    df_melted[['Year', 'Drug Type']] = df_melted['Year_DrugType'].str.extract(r'(\\d{4}) - (.+)')
    df_melted.drop(columns=['Year_DrugType'], inplace=True)
    df_melted.dropna(inplace=True)
    df_melted['Year'] = df_melted['Year'].astype(int)
    df_melted['Seizure Quantity'] = pd.to_numeric(df_melted['Seizure Quantity'], errors='coerce')
    df_melted.dropna(inplace=True)
    
    filtered_df = df_melted[df_melted['Year'] == year_input]
    
    if not filtered_df.empty:
        st.write(f"### Seizure Data for {year_input}")
        st.dataframe(filtered_df.style.format({"Seizure Quantity": "{:.2f}"}))
        
        # Plot the graph
        st.write("### Seizure Quantity by Drug Type")
        fig, ax = plt.subplots(figsize=(10, 5))
        filtered_df.groupby("Drug Type")['Seizure Quantity'].sum().plot(kind='bar', ax=ax, color='skyblue')
        ax.set_xlabel("Drug Type")
        ax.set_ylabel("Seizure Quantity")
        ax.set_title(f"Seizure Quantity by Drug Type in {year_input}")
        st.pyplot(fig)
    else:
        st.warning("No data available for the selected year.")
else:
    st.error("Failed to load data. Please check the API response.")

st.sidebar.write("Made By DEEPTHINKERS")
