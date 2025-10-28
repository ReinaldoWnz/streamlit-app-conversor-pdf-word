import streamlit as st
from pdf2docx import Converter
from io import BytesIO
import os

st.title("Conversor PDF para Word 📄➡️📝 (com formatação original)")

uploaded_files = st.file_uploader("Envie um ou vários PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Converter todos para Word"):
        resultados = []
        erros = []

        for arquivo in uploaded_files:
            try:
                nome_base = os.path.splitext(arquivo.name)[0]
                input_pdf = f"{nome_base}.pdf"
                output_docx = f"{nome_base}.docx"

                # Salvar PDF temporariamente
                with open(input_pdf, "wb") as f:
                    f.write(arquivo.read())

                # Converter com pdf2docx (mantém formatação)
                cv = Converter(input_pdf)
                cv.convert(output_docx, start=0, end=None)
                cv.close()

                # Ler resultado para memória
                with open(output_docx, "rb") as f:
                    buffer = BytesIO(f.read())

                resultados.append((nome_base, buffer))

            except Exception as e:
                erros.append(f"❌ Erro ao converter {arquivo.name}: {str(e)}")

            finally:
                # Limpeza de temporários
                if os.path.exists(input_pdf):
                    os.remove(input_pdf)
                if os.path.exists(output_docx):
                    os.remove(output_docx)

        if resultados:
            st.success("Conversão concluída com formatação mantida!")
            for nome_base, buffer in resultados:
                st.download_button(
                    label=f"📥 Baixar {nome_base}.docx",
                    data=buffer,
                    file_name=f"{nome_base}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        if erros:
            st.warning("Alguns arquivos não puderam ser convertidos:")
            for msg in erros:
                st.text(msg)
