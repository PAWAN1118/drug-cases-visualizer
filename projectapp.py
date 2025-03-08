import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Data URL
url = "https://www.data.gov.in/backend/dms/v1/ogdp/resource/download/603189971/json/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJkYXRhLmdvdi5pbiIsImF1ZCI6ImRhdGEuZ292LmluIiwiaWF0IjoxNzQxNDQ2MzI1LCJleHAiOjE3NDE0NDY2MjUsImRhdGEiOnsibmlkIjoiNjAzMTg5OTcxIn19.rfyiBxRDBSUTr4VMZqfORvE5uRaXSzf8aehzu75cRME"

@st.cache_data
def load_data():
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        if 'data' in data and isinstance(data['data'], list):
            return pd.DataFrame(data['data'])
        else:
            st.error("Data format error.")
            return pd.DataFrame()
    else:
        st.error("Failed to fetch data.")
        return pd.DataFrame()

def preprocess_data(df):
    data2018 = df.iloc[:, 2:13].replace('-', np.nan).astype(float)
    data2019 = df.iloc[:, 13:24].replace('-', np.nan).astype(float)
    data2020 = df.iloc[:, 24:35].replace('-', np.nan).astype(float)
    data2021 = df.iloc[:, 35:45].replace('-', np.nan).astype(float)
    data2022 = df.iloc[:, 45:55].replace('-', np.nan).astype(float)
    
    all_years = pd.concat([data2018, data2019, data2020, data2021, data2022], axis=1)
    all_years.fillna(0, inplace=True)
    return all_years

# Streamlit App UI Enhancements
st.set_page_config(page_title="Drug Cases", layout="wide")
st.title("📊 Drug Cases Analyzer")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Visualization", "Prediction"])

df = load_data()
if not df.empty:
    data = preprocess_data(df)
    
    year = st.sidebar.selectbox("Select Year", ["2018", "2019", "2020", "2021", "2022"])
    
    year_mapping = {
        "2018": data.iloc[:, :11],
        "2019": data.iloc[:, 11:22],
        "2020": data.iloc[:, 22:33],
        "2021": data.iloc[:, 33:43],
        "2022": data.iloc[:, 43:53],
    }
    selected_data = year_mapping.get(year)
    selected_data.columns = [f"Month {i+1}" for i in range(selected_data.shape[1])]
    
    if page == "Overview":
        st.subheader(f"📌 Drug Cases in {year}")
        st.dataframe(selected_data)
        
        # Export Data
        csv = selected_data.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Data as CSV", data=csv, file_name=f"drug_cases_{year}.csv", mime="text/csv")
    
    elif page == "Visualization":
        st.subheader(f"📊 Drug Cases Trend in {year}")
        
        fig = px.line(selected_data.T, markers=True, title=f"Drug Cases Trend ({year})", labels={"index": "Month", "value": "Cases"})
        st.plotly_chart(fig)
    
    elif page == "Prediction":
        # Machine Learning Model
        X = data.iloc[:, :-1]
        y = data.iloc[:, -1]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        st.subheader("📈 Prediction Results")
        st.write(f"✅ Mean Squared Error: {mse:.2f}")
        st.write(f"✅ R-Squared Score: {r2:.2f}")
        
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(y=y_test.values, mode='lines', name='Actual Cases'))
        fig_pred.add_trace(go.Scatter(y=y_pred, mode='lines', name='Predicted Cases'))
        fig_pred.update_layout(title="Actual vs Predicted Cases", xaxis_title="Samples", yaxis_title="Cases")
        st.plotly_chart(fig_pred)

st.sidebar.write("Made By DEEPTHINKERS")
