import streamlit as st
from pdf2docx import Converter
from io import BytesIO
import os
import traceback
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Inches
from tempfile import NamedTemporaryFile

st.title("Conversor PDF ➜ Word 📄➡️📝 (formatação mantida, com fallback automático)")
st.write("Mantém o layout original e usa fallback inteligente caso o PDF tenha imagens corrompidas ou digitalizadas.")

uploaded_files = st.file_uploader("Envie um ou vários PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Converter todos para Word"):
        resultados = []
        erros = []

        for pdf in uploaded_files:
            nome_base = os.path.splitext(pdf.name)[0]
            input_pdf = f"{nome_base}.pdf"
            output_docx = f"{nome_base}.docx"

            try:
                with open(input_pdf, "wb") as f:
                    f.write(pdf.read())

                # PRIMEIRA TENTATIVA - pdf2docx (mantém editável)
                try:
                    cv = Converter(input_pdf)
                    cv.convert(output_docx, start=0, end=None)
                    cv.close()

                # FALLBACK AUTOMÁTICO - PyMuPDF (mantém layout 100%)
                except Exception as e1:
                    if "'Rect' object has no attribute 'get_area'" in str(e1):
                        st.warning(f"⚠️ {pdf.name}: usando modo imagem para preservar layout...")
                        docx = Document()
                        pdf_doc = fitz.open(input_pdf)
                        for i, page in enumerate(pdf_doc):
                            pix = page.get_pixmap(dpi=200)
                            img_temp = NamedTemporaryFile(delete=False, suffix=".png")
                            pix.save(img_temp.name)
                            docx.add_picture(img_temp.name, width=Inches(6.5))
                            if i < len(pdf_doc) - 1:
                                docx.add_page_break()
                            os.remove(img_temp.name)
                        pdf_doc.close()
                        docx.save(output_docx)
                    else:
                        raise e1

                # Lê o resultado final
                with open(output_docx, "rb") as f:
                    buffer = BytesIO(f.read())
                resultados.append((nome_base, buffer))

            except Exception as e:
                erros.append(f"❌ Erro ao converter {pdf.name}: {str(e)}")
                traceback.print_exc()

            finally:
                if os.path.exists(input_pdf):
                    os.remove(input_pdf)
                if os.path.exists(output_docx):
                    os.remove(output_docx)

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
