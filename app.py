import streamlit as st
from io import BytesIO
from docx import Document
from docx.shared import Inches
from tempfile import NamedTemporaryFile
from pdf2image import convert_from_path
import os
import requests
import zipfile
import platform
import traceback

st.title("Conversor PDF ➜ Word (Layout 100% preservado)")
st.write("Cada página do PDF é inserida como imagem no Word, mantendo **toda a formatação original**.")

# Função para garantir que o Poppler esteja disponível
def get_poppler_path():
    poppler_dir = os.path.join(os.getcwd(), "poppler")
    if not os.path.exists(poppler_dir):
        os.makedirs(poppler_dir, exist_ok=True)

    if platform.system() == "Windows":
        poppler_zip = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.07.0/Release-24.07.0-0.zip"
        zip_path = os.path.join(poppler_dir, "poppler.zip")
        if not os.path.exists(os.path.join(poppler_dir, "Library")):
            st.info("📦 Baixando Poppler (necessário para converter PDFs)...")
            with requests.get(poppler_zip, stream=True) as r:
                with open(zip_path, "wb") as f:
                    f.write(r.content)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(poppler_dir)
            os.remove(zip_path)
        return os.path.join(poppler_dir, "Library", "bin")
    else:
        # Para Linux e Streamlit Cloud
        return "/usr/bin"  # O Poppler já costuma existir nesse caminho

uploaded_files = st.file_uploader("Envie um ou vários PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Converter mantendo formatação"):
        resultados = []
        erros = []
        poppler_path = get_poppler_path()

        for pdf in uploaded_files:
            nome_base = os.path.splitext(pdf.name)[0]
            try:
                with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                    tmp_pdf.write(pdf.read())
                    tmp_pdf_path = tmp_pdf.name

                # Converter páginas do PDF em imagens (300 DPI = alta qualidade)
                pages = convert_from_path(tmp_pdf_path, dpi=300, poppler_path=poppler_path)

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
