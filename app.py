import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO

st.title("Conversor PDF ➡️ Word (modo compatível)")

uploaded_file = st.file_uploader("Envie seu PDF", type="pdf")

if uploaded_file is not None:
    if st.button("Converter"):
        pdf_bytes = uploaded_file.read()
        pdf_stream = BytesIO(pdf_bytes)
        doc = Document()

        pdf = fitz.open(stream=pdf_stream, filetype="pdf")
        for page in pdf:
            text = page.get_text("text")
            doc.add_paragraph(text)
            doc.add_page_break()

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.success("Conversão concluída com compatibilidade total no Cloud!")
        st.download_button(
            label="Baixar Word",
            data=buffer,
            file_name="convertido.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
