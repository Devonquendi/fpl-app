from fpl_data.transform import FplApiDataTransformed
import streamlit as st


@st.cache_resource(ttl=3600)
def load_data():
    '''Load and cache data from FPL API'''
    return FplApiDataTransformed()


def display_frame(df):
    '''Modifies the default rendering of Pandas DataFrames
       - displays DataFrames with float columns rounded to 1 decimal place'''
    float_cols = df.select_dtypes(include='float64').columns.values
    st.dataframe(df.style.format(subset=float_cols, formatter='{:.1f}'))


def donate_message():
    """A 'Buy Me a Coffee' message with a link to the donation page displayed
     inline"""
    html_content = """
    <div style="display: flex; align-items: center; gap: 10px;">
        <span>If you like this work and want to support me</span>
        <a
            href="https://www.buymeacoffee.com/jamesbleslie"
            target="_blank"
            style="
                background-color: #FFDD00;
                color: black;
                padding: 10px 20px;
                text-decoration: none;
                font-weight: bold;
                border-radius: 5px;
            "
        >
            Buy Me a Coffee ☕
        </a>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
