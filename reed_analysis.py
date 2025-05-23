# analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px
from db import run_query

st.set_page_config(layout="wide")

def load_all_data():
    return run_query("SELECT * FROM reed_inventory")

def load_data_by_date(selected_date):
    return run_query(
        "SELECT CourseId, title, provider, student FROM reed_inventory WHERE date = %s",
        [selected_date]
    )

def show_analysis():
    df = load_all_data()

    st.title("📊 Dashboard")

    # --- Top Providers ---
    course_count_df = df.groupby("provider")['CourseId'].nunique().sort_values(ascending=False).head(10).reset_index()
    course_count_df.rename(columns={'CourseId': 'course_count'}, inplace=True)

    student_count_df = df.groupby("provider")['student'].sum().sort_values(ascending=False).head(10).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(course_count_df, x='course_count', y='provider', orientation='h',
                      title='Top 10 Providers by Course Count')
        fig1.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(student_count_df, x='student', y='provider', orientation='h',
                      title='Top 10 Providers by Student Count')
        fig2.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("📅 Filter and View Data")

    col1, col2 = st.columns(2)

    with col1:
        selected_date = st.date_input("Select a Date")
    with col2:
        keyword = st.text_input("Search in Title")

    all_providers = sorted(df['provider'].dropna().unique().tolist())
    selected_providers = st.multiselect("Filter by Provider(s)", options=all_providers)

    if selected_date:
        date_df = load_data_by_date(selected_date)
    else:
        date_df = pd.DataFrame()

    if not date_df.empty:
        if selected_providers:
            date_df = date_df[date_df['provider'].isin(selected_providers)]

        if keyword.strip():
            date_df = date_df[date_df['title'].str.contains(keyword.strip(), case=False, na=False)]

        st.markdown(f"### 📄 Data for {selected_date.strftime('%Y-%m-%d')} ({len(date_df)} records)")
        display_df = date_df.sort_values(by='student', ascending=False)
        st.dataframe(display_df, use_container_width=True, height=600)

def show_analysis_date_range():
    df = load_all_data()
    df['date'] = pd.to_datetime(df['date']).dt.date
    all_dates = sorted(df['date'].unique())

    st.title("📈 Compare Two Dates")
    col1, col2 = st.columns(2)
    with col1:
        date1 = st.date_input("Start Date", value=all_dates[0], min_value=all_dates[0], max_value=all_dates[-1])
    with col2:
        date2 = st.date_input("End Date", value=all_dates[-1], min_value=all_dates[0], max_value=all_dates[-1])

    if date1 > date2:
        st.warning("⚠️ Start date should be before end date.")
        return

    df1 = df[df['date'] == date1].copy()
    df2 = df[df['date'] == date2].copy()

    df1 = df1[['CourseId', 'title', 'provider', 'student']].rename(columns={'student': 'student_date1'})
    df2 = df2[['CourseId', 'title', 'provider', 'student']].rename(columns={'student': 'student_date2'})

    merged = pd.merge(df1, df2, on='CourseId', how='outer', suffixes=('_d1', '_d2'))

    merged['title'] = merged['title_d1'].combine_first(merged['title_d2'])
    merged['provider'] = merged['provider_d1'].combine_first(merged['provider_d2'])
    merged.drop(columns=['title_d1', 'title_d2', 'provider_d1', 'provider_d2'], inplace=True)

    merged['difference'] = merged['student_date2'] - merged['student_date1']

    # Calculate % change safely
    merged['percent_change'] = merged.apply(
        lambda row: ((row['difference'] / row['student_date1']) * 100)
        if pd.notnull(row['student_date1']) and row['student_date1'] != 0 else None,
        axis=1
    )

    # Round and fill NaN
    merged['percent_change'] = merged['percent_change'].round(2)
    merged['percent_change'] = merged['percent_change'].fillna("N/A")

    # Rearranging columns
    merged = merged[['CourseId', 'title', 'provider', 'student_date1', 'student_date2', 'difference', 'percent_change']]

    st.markdown("### 🔧 Filters")

    with col1:
        selected_providers = st.multiselect("Filter by Provider(s)",
                                            options=sorted(df['provider'].dropna().unique().tolist()))
    with col2:
        keyword = st.text_input("Search by Keyword in Title")

    filtered = merged.copy()
    if selected_providers:
        filtered = filtered[filtered['provider'].isin(selected_providers)]
    if keyword:
        filtered = filtered[filtered['title'].str.contains(keyword, case=False, na=False)]

    filtered = filtered.sort_values(by='difference', ascending=False)
    st.markdown(f"### 📊 Comparison: {date1} → {date2}")
    st.dataframe(filtered, use_container_width=True)
