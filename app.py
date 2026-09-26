import streamlit as st
from analyzer import review_code

st.set_page_config(
    page_title="Intelligent Code Review Coach",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Intelligent Code Review Coach")
st.markdown("Automated static code review, bug detection, and security guidance.")

default_snippet = '''import os

def process_data(payload, cache=[]):
    api_key = "AIzaSyD-fakeKeyExample12345"
    try:
        result = eval(payload)
    except:
        result = None
    return result
'''

code_input = st.text_area("Paste code snippet to analyze:", value=default_snippet, height=220)

if st.button("Run Code Review", type="primary"):
    if not code_input.strip():
        st.warning("Please provide code to analyze.")
    else:
        report = review_code(code_input)

        st.subheader("Analysis Summary")
        col1, col2 = st.columns(2)
        col1.metric("Lines of Code", report["total_lines"])
        col2.metric("Issues Found", report["total_issues"])

        st.divider()

        if report["total_issues"] == 0:
            st.success("✅ No issues detected. Clean and ready to go!")
        else:
            for item in report["issues"]:
                badge = {
                    "Critical": "🚨 Critical",
                    "High": "⚠️ High",
                    "Medium": "⚡ Medium",
                    "Low": "ℹ️ Low"
                }.get(item["severity"], item["severity"])

                with st.expander(f"Line {item['line']} — {item['type']} ({badge})"):
                    st.write(f"**Issue:** {item['message']}")
                    st.info(f"**Recommended Fix:** {item['fix']}")
