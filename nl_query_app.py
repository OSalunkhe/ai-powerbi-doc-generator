import streamlit as st
from ask_question import generate_sql, is_safe_select, run_query, summarize_result, extract_assumption_note

st.set_page_config(page_title="Ask Your Power BI Data", layout="wide")
st.title("Ask Your Power BI Data")
st.write("Type a question in plain English about the data exported from your Power BI model.")

question = st.text_input("Your question", placeholder="e.g. What were total sales by region?")

if st.button("Ask") and question:
    with st.spinner("Generating query..."):
        sql = generate_sql(question)

    st.subheader("Generated SQL")
    st.code(sql, language="sql")

    note = extract_assumption_note(sql)
    if note:
        st.warning(f"Assumption made by the model: {note.replace('-- ', '')}")

    if not is_safe_select(sql):
        st.error("This query didn't pass the safety check and was not run.")
    else:
        try:
            result = run_query(sql)
            st.subheader("Result")
            st.dataframe(result)

            with st.spinner("Summarizing..."):
                summary = summarize_result(question, result, note)
            st.subheader("Answer")
            st.write(summary)
        except Exception as e:
            st.error(f"Query failed: {e}")