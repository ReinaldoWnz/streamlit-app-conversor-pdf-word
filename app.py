import streamlit as st
from io import BytesIO
from docx import Document
from docx.shared import Inches
from tempfile import NamedTemporaryFile
import fitz  # PyMuPDF
import os
import traceback

st.title("Conversor PDF ➜ Word (Layout 100% preservado)")
st.write("Mantém **toda a formatação** do PDF inserindo cada página como imagem no Word — compatível com o Streamlit Cloud.")

uploaded_files = st.file_uploader("Envie um ou vários PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Converter mantendo formatação"):
        resultados = []
        erros = []

        for pdf in uploaded_files:
            nome_base = os.path.splitext(pdf.name)[0]
            try:
                with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                    tmp_pdf.write(pdf.read())
                    tmp_pdf_path = tmp_pdf.name

                # Abrir PDF via PyMuPDF (fitz)
                doc_pdf = fitz.open(tmp_pdf_path)
                docx = Document()

                for i, page in enumerate(doc_pdf):
                    # Renderiza cada página como imagem
                    pix = page.get_pixmap(dpi=200)  # 200dpi mantém ótima qualidade e performance
                    img_temp = NamedTemporaryFile(delete=False, suffix=".png")
                    pix.save(img_temp.name)

                    # Adiciona imagem ao DOCX
                    docx.add_picture(img_temp.name, width=Inches(6.5))
                    if i < len(doc_pdf) - 1:
                        docx.add_page_break()

                    os.remove(img_temp.name)

                doc_pdf.close()

                # Salva e prepara o download
                output_docx = f"{nome_base}.docx"
                docx.save(output_docx)
                with open(output_docx, "rb") as f:
                    buffer = BytesIO(f.read())
                resultados.append((nome_base, buffer))

            except Exception as e:
                erros.append(f"❌ Erro ao converter {pdf.name}: {str(e)}")
                traceback.print_exc()

            finally:
                if os.path.exists(tmp_pdf_path):
                    os.remove(tmp_pdf_path)
                if os.path.exists(f"{nome_base}.docx"):
                    os.remove(f"{nome_base}.docx")

        # Exibe resultados
        if resultados:
            st.success("Conversão concluída com formatação preservada!")
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
