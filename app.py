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

            # ⚠️ Ler o conteúdo em memória antes de salvar
            pdf_bytes = arquivo.read()
            if not pdf_bytes:
                continue  # evita erro de arquivo vazio

            # Salvar PDF no disco
            with open(input_pdf, "wb") as f:
                f.write(pdf_bytes)

            # Executar conversão em bloco independente
            try:
                cv = Converter(input_pdf)
                cv.convert(output_docx, start=0, end=None)
                cv.close()

                # Ler o DOCX gerado
                with open(output_docx, "rb") as f:
                    buffer = BytesIO(f.read())

                resultados.append((nome_base, buffer))

            except Exception as e:
                st.warning(f"❌ Falha ao converter {arquivo.name}: {e}")

            finally:
                if os.path.exists(input_pdf):
                    os.remove(input_pdf)
                if os.path.exists(output_docx):
                    os.remove(output_docx)

        # Exibe resultados
        if resultados:
            st.success("Conversão concluída com formatação mantida!")
            for nome_base, buffer in resultados:
                st.download_button(
                    label=f"📥 Baixar {nome_base}.docx",
                    data=buffer,
                    file_name=f"{nome_base}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
