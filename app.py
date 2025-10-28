import streamlit as st
from io import BytesIO
from pdf2image import convert_from_path
from docx import Document
from docx.shared import Inches
import os
import traceback
from tempfile import NamedTemporaryFile

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
                # Salvar PDF temporariamente
                with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                    tmp_pdf.write(pdf.read())
                    tmp_pdf_path = tmp_pdf.name

                # Converter páginas do PDF em imagens (300 DPI para boa qualidade)
                pages = convert_from_path(tmp_pdf_path, dpi=300)

                # Criar DOCX
                doc = Document()
                for i, page in enumerate(pages):
                    img_temp = NamedTemporaryFile(delete=False, suffix=".jpg")
                    page.save(img_temp.name, "JPEG")
                    doc.add_picture(img_temp.name, width=Inches(6.5))  # largura padrão da página A4
                    if i < len(pages) - 1:
                        doc.add_page_break()
                    os.remove(img_temp.name)

                # Salvar resultado em memória
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

        # Resultados
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
