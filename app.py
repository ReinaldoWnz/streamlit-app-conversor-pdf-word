import streamlit as st
from pdf2docx import Converter
from io import BytesIO
import os

st.title("Conversor PDF para Word 📄➡️📝 (com formatação original)")

uploaded_files = st.file_uploader(
    "Envie um ou vários PDFs",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Converter todos para Word"):
        resultados = []

        for arquivo in uploaded_files:
            nome_base = os.path.splitext(arquivo.name)[0]
            input_pdf = f"{nome_base}.pdf"
            output_docx = f"{nome_base}.docx"

            # Salva o PDF temporariamente
            with open(input_pdf, "wb") as f:
                f.write(arquivo.read())

            # Converte com pdf2docx (mantém a formatação)
            cv = Converter(input_pdf)
            cv.convert(output_docx, start=0, end=None)
            cv.close()

            # Lê o DOCX em memória
            with open(output_docx, "rb") as f:
                buffer = BytesIO(f.read())

            # Adiciona ao resultado
            resultados.append((nome_base, buffer))

            # Remove arquivos temporários
            os.remove(input_pdf)
            os.remove(output_docx)

        st.success("Conversão concluída com formatação mantida!")

        # Cria um botão de download para cada arquivo
        for nome_base, buffer in resultados:
            st.download_button(
                label=f"📥 Baixar {nome_base}.docx",
                data=buffer,
                file_name=f"{nome_base}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
