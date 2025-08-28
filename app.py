import streamlit as st
import pdfplumber
from docx import Document
from io import BytesIO

st.title("Conversor PDF para Word 📄➡️📝")

uploaded_file = st.file_uploader("Envie seu PDF", type="pdf")

if uploaded_file is not None:
    if st.button("Converter para Word"):
        doc = Document()
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    doc.add_paragraph(text)
        
        # Salvar em memória
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.success("Conversão concluída!")
        st.download_button(
            label="Baixar Word",
            data=buffer,
            file_name="convertido.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
