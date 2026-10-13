
import streamlit as st
from analyzer import review_code

st.set_page_config(
    page_title="Intelligent Code Review Coach",
    page_icon="🔍",
    layout="wide"
)

st.title("Intelligent Code Review Coach")
st.write("Analyze Python code for security risks, bugs, and code-quality issues.")

code = st.text_area(
    "Paste your Python code",
    height=300,
    placeholder="Paste Python code here..."
)

if st.button("Analyze Code", type="primary"):
    if not code.strip():
        st.warning("Please paste some Python code first.")
    else:
        result = review_code(code)

        total = result["total_issues"]
        critical = sum(
            issue["severity"] == "Critical"
            for issue in result["issues"]
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Lines of Code", result["total_lines"])
        col2.metric("Total Issues", total)
        col3.metric("Critical Issues", critical)

        if total == 0:
            st.success("No issues detected by the current rules.")
        else:
            st.subheader("Review Results")

            for issue in result["issues"]:
                with st.expander(
                    f"Line {issue['line']} | "
                    f"{issue['severity']} | "
                    f"{issue['type']}"
                ):
                    st.write(issue["message"])
                    st.markdown("**Suggested fix**")
                    st.write(issue["fix"])
