import streamlit as st
from analyzer import review_code

st.set_page_config(
    page_title="Intelligent Code Review Coach",
    page_icon="🔍",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e222d;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #333a4d;
    }
    .badge-critical { background-color: #ff4b4b; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-high { background-color: #ffa116; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-medium { background-color: #ffcc00; color: black; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-low { background-color: #00c0f2; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🔍 Intelligent Code Review Coach")
st.caption("AI-assisted static code analysis, security auditing, and quality grading.")

# Sidebar preset selector
st.sidebar.header("Demo Snippets")
preset = st.sidebar.selectbox(
    "Load test sample:",
    ["Custom Code", "High Risk Vulnerabilities", "Clean Python Code"]
)

default_code = """import os
import sys

api_key = "AIzaSyD-sampleSecurityKey999"

def process_batch(items, cache=[]):
    list = [1, 2, 3]
    if items == None:
        return None
    try:
        output = eval(items)
    except:
        output = None
    print(output)
    return output
"""

if preset == "High Risk Vulnerabilities":
    code_input = default_code
elif preset == "Clean Python Code":
    code_input = '''import json
from typing import Optional, List, Any

def process_batch(items: str, cache: Optional[List[Any]] = None) -> Optional[Any]:
    """Safely decode and parse inputs without mutable defaults or dangerous eval."""
    if cache is None:
        cache = []
    
    if items is None:
        return None

    try:
        return json.loads(items)
    except json.JSONDecodeError:
        return None
'''
else:
    code_input = default_code

col_left, col_right = st.columns([1.1, 0.9])

with col_left:
    st.subheader("Source Code Input")
    user_code = st.text_area("Paste Python code snippet:", value=code_input, height=380)
    analyze_btn = st.button("🚀 Analyze Code", type="primary", use_container_width=True)

if analyze_btn or user_code:
    results = review_code(user_code)
    total_issues = results["total_issues"]
    total_lines = results["total_lines"]
    
    # Calculate simple quality score (100 minus penalty)
    score = max(0, 100 - (total_issues * 15))

    with col_right:
        st.subheader("Analysis Summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("Lines of Code", total_lines)
        m2.metric("Total Issues", total_issues)
        m3.metric("Health Score", f"{score}/100")

        if total_issues == 0:
            st.success("✅ Clean code! No security risks or style defects found.")
        else:
            # Interactive Filter
            filter_sev = st.multiselect(
                "Filter by Severity:",
                ["Critical", "High", "Medium", "Low"],
                default=["Critical", "High", "Medium", "Low"]
            )

            filtered_issues = [i for i in results["issues"] if i["severity"] in filter_sev]

            for item in filtered_issues:
                sev = item["severity"]
                icon = "🚨" if sev == "Critical" else ("⚠️" if sev in ("High", "Medium") else "ℹ️")
                
                with st.expander(f"{icon} Line {item['line']} — {item['type']} ({sev})", expanded=True):
                    st.write(f"**Issue:** {item['message']}")
                    st.info(f"💡 **Suggested Fix:** {item['fix']}")
