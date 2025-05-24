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
            st.write("Original CSV Preview:", df.head())

            csv_columns = list(df.columns)
            required_columns = {
                'CourseId': None,
                'title': None,
                'subTitle': None,
                'provider': None,
                'student': None,
                'price': None,
                'link': None,
                'date': None,
            }

            st.markdown("### Map CSV Columns to Database Columns")

            for col in required_columns:
                required_columns[col] = st.selectbox(f"Map database column **{col}** to:", options=csv_columns, key=col)

            # Preview mapped DataFrame
            mapped_df = pd.DataFrame({
                db_col: df[csv_col]
                for db_col, csv_col in required_columns.items()
            })

            st.markdown("### Mapped Data Preview")
            st.dataframe(mapped_df.head(), use_container_width=True)

            # Parse date field
            try:
                mapped_df['date'] = pd.to_datetime(mapped_df['date'], errors='coerce').dt.date
            except:
                st.warning("Date parsing failed. Please check your column mapping.")

            if st.button("Upload to Database"):
                conn = get_connection()
                cursor = conn.cursor()
                inserted = 0
                skipped = 0

                for _, row in mapped_df.iterrows():
                    if pd.isnull(row['date']) or pd.isnull(row['CourseId']):
                        skipped += 1
                        continue

                    cursor.execute(
                        "SELECT COUNT(*) FROM reed_inventory WHERE CourseId = %s AND date = %s",
                        (row['CourseId'], row['date'])
                    )
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("""
                            INSERT INTO reed_inventory 
                            (CourseId, title, subTitle, provider, student, price, link, date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            row['CourseId'], row['title'], row['subTitle'], row['provider'],
                            int(row['student']), float(row['price']),
                            row['link'], row['date']
                        ))
                        inserted += 1
                    else:
                        skipped += 1

                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"Upload complete. Inserted: {inserted}, Skipped (duplicates or invalid rows): {skipped}")

        except Exception as e:
            st.error(f"Error: {e}")
