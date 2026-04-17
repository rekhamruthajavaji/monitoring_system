import json
import streamlit as st
import os
import pandas as pd
import time

st.set_page_config(layout="wide")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMON_JSON = os.path.join(BASE_DIR, "shared", "monitoring.json")

st.title("📊 Unified Monitoring Dashboard")

show_chart = st.checkbox("📊 Show Charts")
auto_refresh = st.checkbox("⏱️ Auto Refresh (5 sec)")

if not os.path.exists(COMMON_JSON):
    st.error("File not found")
    st.stop()

with open(COMMON_JSON) as f:
    data = json.load(f)

servers = data.get("servers", {})

for server_name, info in servers.items():
    st.markdown("---")
    st.header(server_name)

    passing = 1 if info["status"] == "SUCCESS" else 0
    failing = 0 if info["status"] == "SUCCESS" else 1

    col1, col2 = st.columns(2)
    col1.metric("Passing", passing)
    col2.metric("Failing", failing)

    st.write("Last Run:", info["last_run"])

    col1, col2 = st.columns(2)

    with col1:
        st.write("Input:", info["input"])
        df = pd.DataFrame(info["input_types"].items(), columns=["Type","Count"])
        st.table(df)
        if show_chart:
            st.bar_chart(df.set_index("Type"))

    with col2:
        st.write("Output:", info["output"])
        df2 = pd.DataFrame(info["output_types"].items(), columns=["Type","Count"])
        st.table(df2)
        if show_chart:
            st.bar_chart(df2.set_index("Type"))

    if info["status"] == "SUCCESS":
        st.success("SUCCESS")
    else:
        st.error("FAIL")

if auto_refresh:
    time.sleep(5)
    st.rerun()
