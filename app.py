import streamlit as st
from io import BytesIO
from docx import Document
from docx.shared import Inches
import os
import traceback
from tempfile import NamedTemporaryFile
import platform
import subprocess

# Instala Poppler automaticamente, se necessário
try:
    from pdf2image import convert_from_path
except ImportError:
    st.warning("Baixando dependências necessárias... (isso pode demorar alguns segundos)")
    subprocess.run(["pip", "install", "pdf2image", "python-docx", "Pillow"], check=True)
    from pdf2image import convert_from_path

if platform.system() == "Linux":
    try:
        subprocess.run(["which", "pdftoppm"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        st.warning("Instalando Poppler (necessário para processar PDFs)...")
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(["apt-get", "install", "-y", "poppler-utils"], check=True)

st.title("Conversor PDF ➜ Word (Layout 100% preservado)")
st.write("Este modo insere cada página do PDF como imagem dentro do Word — mantendo toda a formatação original.")

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

                pages = convert_from_path(tmp_pdf_path, dpi=300)

                doc = Document()
                for i, page in enumerate(pages):
                    img_temp = NamedTemporaryFile(delete=False, suffix=".jpg")
                    page.save(img_temp.name, "JPEG")
                    doc.add_picture(img_temp.name, width=Inches(6.5))
                    if i < len(pages) - 1:
                        doc.add_page_break()
                    os.remove(img_temp.name)

                output_docx = f"{nome_base}.docx"
                doc.save(output_docx)
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
