import streamlit as st

NEW_URL = "https://fplstat.app"

st.set_page_config(page_title="FPLstat has moved", page_icon="⚽")

st.title("⚽ FPLstat has moved")
st.write(f"This app now lives at **[fplstat.app]({NEW_URL})**. Please update your bookmarks.")
st.link_button("Go to fplstat.app", NEW_URL, type="primary")
