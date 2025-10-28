import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Inches
from io import BytesIO
from tempfile import NamedTemporaryFile
import os

st.title("Conversor PDF ➜ Word 📄➡️📝 (layout 100% preservado)")

uploaded_files = st.file_uploader("Envie um ou vários PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Converter todos para Word"):
        resultados = []

        for arquivo in uploaded_files:
            nome_base = os.path.splitext(arquivo.name)[0]
            input_pdf = f"{nome_base}.pdf"
            output_docx = f"{nome_base}.docx"

            # Salvar PDF temporariamente
            with open(input_pdf, "wb") as f:
                f.write(arquivo.read())

            # Converter com PyMuPDF (gera imagem por página)
            doc = Document()
            pdf = fitz.open(input_pdf)

            for i, page in enumerate(pdf):
                pix = page.get_pixmap(dpi=200)  # alta qualidade
                img_temp = NamedTemporaryFile(delete=False, suffix=".png")
                pix.save(img_temp.name)

                doc.add_picture(img_temp.name, width=Inches(6.5))
                if i < len(pdf) - 1:
                    doc.add_page_break()

                os.remove(img_temp.name)

            pdf.close()
            doc.save(output_docx)

            with open(output_docx, "rb") as f:
                buffer = BytesIO(f.read())

            resultados.append((nome_base, buffer))
            os.remove(input_pdf)
            os.remove(output_docx)

        st.success("Conversão concluída com layout preservado!")
        for nome_base, buffer in resultados:
            st.download_button(
                label=f"📥 Baixar {nome_base}.docx",
                data=buffer,
                file_name=f"{nome_base}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
