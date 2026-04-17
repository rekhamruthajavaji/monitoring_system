import json
import streamlit as st
import os
import pandas as pd
import time

st.set_page_config(layout="wide")

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMON_JSON = os.path.join(BASE_DIR, "shared", "monitoring.json")

st.title("📊 Unified Monitoring Dashboard")

show_chart = st.checkbox("📊 Show Charts")
auto_refresh = st.checkbox("⏱️ Auto Refresh (5 sec)")

# Function to format file size
def format_size(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{round(size/1024, 2)} KB"
    else:
        return f"{round(size/(1024*1024), 2)} MB"

# Check file
if not os.path.exists(COMMON_JSON):
    st.error("File not found. Run backend first.")
    st.stop()

# Load JSON
with open(COMMON_JSON) as f:
    data = json.load(f)

servers = data.get("servers", {})

# Display each server
for server_name, info in servers.items():
    st.markdown("---")
    st.header(server_name)

    # Passing / Failing
    passing = 1 if info["status"] == "SUCCESS" else 0
    failing = 0 if info["status"] == "SUCCESS" else 1

    col1, col2 = st.columns(2)
    col1.metric("Passing", passing)
    col2.metric("Failing", failing)

    st.write("🕒 Last Run:", info["last_run"])

    col1, col2 = st.columns(2)

    # ================= INPUT =================
    with col1:
        st.subheader("📥 Input")
        st.metric("Input Files", info["input"])
        st.metric("Input Size", format_size(info.get("input_size", 0)))

        # 🔥 File-wise sizes
        st.write("📄 Input File Sizes:")
        input_files = info.get("input_files", [])
        if input_files:
            df_input_files = pd.DataFrame(input_files)
            df_input_files["size"] = df_input_files["size"].apply(format_size)
            st.table(df_input_files)
        else:
            st.write("No input files found")

        # 🔥 Type-wise table (Count + Size)
        input_types = info.get("input_types", {})
        input_sizes = info.get("input_type_sizes", {})

        df = pd.DataFrame([
            {
                "Type": t,
                "Count": input_types[t],
                "Size": format_size(input_sizes.get(t, 0))
            }
            for t in input_types
        ])

        st.write("📊 Input File Types:")
        st.table(df)

        if show_chart and not df.empty:
            st.bar_chart(df.set_index("Type")["Count"])

    # ================= OUTPUT =================
    with col2:
        st.subheader("📤 Output")
        st.metric("Output Files", info["output"])
        st.metric("Output Size", format_size(info.get("output_size", 0)))

        # 🔥 File-wise sizes
        st.write("📄 Output File Sizes:")
        output_files = info.get("output_files", [])
        if output_files:
            df_output_files = pd.DataFrame(output_files)
            df_output_files["size"] = df_output_files["size"].apply(format_size)
            st.table(df_output_files)
        else:
            st.write("No output files found")

        # 🔥 Type-wise table (Count + Size)
        output_types = info.get("output_types", {})
        output_sizes = info.get("output_type_sizes", {})

        df2 = pd.DataFrame([
            {
                "Type": t,
                "Count": output_types[t],
                "Size": format_size(output_sizes.get(t, 0))
            }
            for t in output_types
        ])

        st.write("📊 Output File Types:")
        st.table(df2)

        if show_chart and not df2.empty:
            st.bar_chart(df2.set_index("Type")["Count"])

    # STATUS
    if info["status"] == "SUCCESS":
        st.success("✅ SUCCESS")
    else:
        st.error("❌ FAIL")

# Auto refresh
if auto_refresh:
    time.sleep(5)
    st.rerun()