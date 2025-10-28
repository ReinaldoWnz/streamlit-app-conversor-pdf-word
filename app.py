import streamlit as st
from pdf2docx import Converter
from io import BytesIO
import os

st.title("Conversor PDF para Word 📄➡️📝 (com formatação)")
st.write("Envie **um ou vários PDFs** e baixe os arquivos Word convertidos separadamente.")

# Permite múltiplos uploads
uploaded_files = st.file_uploader("Envie seus PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Converter todos para Word"):
        resultados = []

        for pdf in uploaded_files:
            nome_base = os.path.splitext(pdf.name)[0]
            input_pdf = f"{nome_base}.pdf"
            output_docx = f"{nome_base}.docx"

            # Salvar PDF temporariamente
            with open(input_pdf, "wb") as f:
                f.write(pdf.read())

            # Converter PDF -> DOCX
            cv = Converter(input_pdf)
            cv.convert(output_docx, start=0, end=None)
            cv.close()

            # Ler DOCX em memória para download
            with open(output_docx, "rb") as f:
                buffer = BytesIO(f.read())

            resultados.append((nome_base, buffer))

            # Remover arquivos temporários
            os.remove(input_pdf)
            os.remove(output_docx)

        st.success("Conversão concluída! Baixe abaixo seus arquivos:")

        # Gera botão de download para cada DOCX
        for nome_base, buffer in resultados:
            st.download_button(
                label=f"📥 Baixar {nome_base}.docx",
                data=buffer,
                file_name=f"{nome_base}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
