# csv_uploader.py
import pandas as pd
import streamlit as st
from db import get_connection
from datetime import datetime

def import_csv_with_mapping():
    st.subheader("Upload Reed Inventory CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            # Parse the date column
            df['date'] = pd.to_datetime(df['date'], format="%m/%d/%Y").dt.date

            st.write("Preview:", df.head())

            if st.button("Upload to Database"):
                conn = get_connection()
                cursor = conn.cursor()
                inserted = 0
                skipped = 0

                for _, row in df.iterrows():
                    # Check for duplicates
                    cursor.execute(
                        "SELECT COUNT(*) FROM reed_inventory WHERE CourseId = %s AND date = %s",
                        (row['CourseId'], row['date'])
                    )
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("""
                            INSERT INTO reed_inventory 
                            (CourseId, title, subTitle, provider, student, price, wasPrice, link, date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            row['CourseId'], row['title'], row['subTitle'], row['provider'],
                            int(row['student']), float(row['price']), float(row['wasPrice']),
                            row['link'], row['date']
                        ))
                        inserted += 1
                    else:
                        skipped += 1

                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"Upload complete. Inserted: {inserted}, Skipped (duplicates): {skipped}")
        except Exception as e:
            st.error(f"Error: {e}")
