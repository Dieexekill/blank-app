import sys

print(sys.executable)

import streamlit as st
from pypdf import PdfReader, PdfWriter
import io

st.set_page_config(page_title="PDF File Merger", page_icon="📄", layout="centered")

st.title("📄 PDF File Merger")
st.write("Upload two PDF files to merge them together into a single document.")

# File upload widgets
col1, col2 = st.columns(2)

with col1:
    file1 = st.file_uploader("Upload First PDF", type=["pdf"])

with col2:
    file2 = st.file_uploader("Upload Second PDF", type=["pdf"])

if file1 and file2:
    try:
        # Read the PDFs using pypdf
        reader1 = PdfReader(file1)
        reader2 = PdfReader(file2)

        # Get page counts for the metrics
        pages1 = len(reader1.pages)
        pages2 = len(reader2.pages)

        st.success("✅ PDFs loaded successfully!")

        # Combine the PDFs
        merger = PdfWriter()

        # Add pages from the first file
        for page in reader1.pages:
            merger.add_page(page)

        # Add pages from the second file
        for page in reader2.pages:
            merger.add_page(page)

        # Display document metrics
        st.subheader("Document Summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("File 1 Pages", pages1)
        m2.metric("File 2 Pages", pages2)
        m3.metric("Total Merged Pages", len(merger.pages))

        # Save the merged PDF to a temporary buffer in memory
        buffer = io.BytesIO()
        merger.write(buffer)
        data_to_download = buffer.getvalue()
        buffer.close()

        # Download button
        st.download_button(
            label="📥 Download Merged PDF",
            data=data_to_download,
            file_name="merged_document.pdf",
            mime="application/pdf",
            type="primary"
        )

    except Exception as e:
        st.error(f"An error occurred while processing the files: {e}")
