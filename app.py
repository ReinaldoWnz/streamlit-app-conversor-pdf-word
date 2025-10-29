import streamlit as st
from pdf2docx import Converter
from io import BytesIO

st.title("Conversor PDF para Word 📄➡️📝 (com formatação)")

uploaded_file = st.file_uploader("Envie seu PDF", type="pdf")

if uploaded_file is not None:
    if st.button("Converter para Word"):
        # Salvar temporariamente
        input_pdf = "temp.pdf"
        with open(input_pdf, "wb") as f:
            f.write(uploaded_file.read())

        # Converter com pdf2docx
        output_docx = "convertido.docx"
        cv = Converter(input_pdf)
        cv.convert(output_docx, start=0, end=None)
        cv.close()

        # Ler em memória
        with open(output_docx, "rb") as f:
            buffer = BytesIO(f.read())

        st.success("Conversão concluída com formatação mantida!")
        st.download_button(
            label="Baixar Word",
            data=buffer,
            file_name="convertido.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
