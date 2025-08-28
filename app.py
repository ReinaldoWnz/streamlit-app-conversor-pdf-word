import streamlit as st
import pypandoc
from io import BytesIO
import os

st.title("Conversor PDF para Word 📄➡️📝")

# Garante que o Pandoc esteja disponível
try:
    pypandoc.get_pandoc_path()
except OSError:
    st.write("📥 Baixando o Pandoc...")
    pypandoc.download_pandoc()

uploaded_file = st.file_uploader("Envie seu PDF", type="pdf")

if uploaded_file is not None:
    if st.button("Converter para Word"):
        # Salvar PDF temporário
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())

        # Converter PDF para DOCX
        output_file = "convertido.docx"
        pypandoc.convert_file("temp.pdf", "docx", outputfile=output_file)

        # Ler convertido em memória
        with open(output_file, "rb") as f:
            buffer = BytesIO(f.read())

        st.success("Conversão concluída!")
        st.download_button(
            label="Baixar Word",
            data=buffer,
            file_name="convertido.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
