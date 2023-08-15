import streamlit as st


def display_frame(df):
    '''Modifies the default rendering of Pandas DataFrames
       - displays DataFrames with float columns rounded to 1 decimal place'''
    float_cols = df.select_dtypes(include='float64').columns.values
    st.dataframe(df.style.format(subset=float_cols, formatter='{:.1f}'))