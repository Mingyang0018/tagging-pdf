import streamlit as st
import fitz  # PyMuPDF
import json
import uuid
import re
import io
import pandas as pd
from streamlit_ace import st_ace

st.set_page_config(page_title="PDF Tagging Tool", layout="centered")
st.title("PDF Tagging Tool")

uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"])

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    pages = [page.get_text("text") for page in doc]

    # Add page number headers to each page text
    pages_with_numbers = [f"--- {i+1} ---\n{page}" for i, page in enumerate(pages)]
    # Join all pages into one text block for ACE editor
    joined_text = "\n\n".join(pages_with_numbers)

    # Display editable ACE editor with full document text
    edited = st_ace(
        value=joined_text,
        language="text",
        theme="chrome",
        height=800,
        key="ace-editor",
        auto_update=True  # Auto update on text change, no APPLY button needed
    )

    if edited:
        # Split edited text by page markers to maintain correct pagination
        edited_text = re.split(r'^--- \d+ ---', edited, flags=re.MULTILINE)[1:]
        # Strip leading/trailing whitespace and ignore empty pages
        edited_text = [text.strip() for text in edited_text if text.strip()]

        export_data = {
            "document": uploaded_file.name,
            "edited_text": edited_text
        }

        # Prepare JSON export data with indentation and Unicode support
        json_data = json.dumps(export_data, indent=3, ensure_ascii=False)

        # JSON download button
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"{uploaded_file.name}_{uuid.uuid4()}.json",
            mime="application/json"
        )

        # Prepare DataFrame for CSV export: page_number and text columns
        df = pd.DataFrame({
            "page_number": list(range(1, len(edited_text) + 1)),
            "text": edited_text
        })

        # Use StringIO buffer to generate CSV content in memory
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        # CSV download button
        st.download_button(
            label="Download CSV",
            data=csv_buffer.getvalue(),
            file_name=f"{uploaded_file.name}_{uuid.uuid4()}.csv",
            mime="text/csv"
        )
