import streamlit as st
from pdf2docx import Converter
from io import BytesIO
from docx import Document
import os
import pdfplumber
import traceback

st.title("Conversor PDF para Word 📄➡️📝 (com fallback inteligente)")
st.write("Converte PDFs mantendo a formatação quando possível, e extrai o texto bruto quando necessário.")

uploaded_files = st.file_uploader("Envie seus PDFs", type="pdf", accept_multiple_files=True)

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

                # 1️⃣ TENTATIVA PRINCIPAL: pdf2docx
                try:
                    cv = Converter(input_pdf)
                    cv.convert(output_docx, start=0, end=None)
                    cv.close()

                # 2️⃣ FALLBACK: pdfplumber -> texto bruto
                except Exception as e1:
                    st.warning(f"⚠️ {pdf.name} falhou com pdf2docx, tentando extrair texto...")

                    doc = Document()
                    with pdfplumber.open(input_pdf) as p:
                        for page in p.pages:
                            text = page.extract_text()
                            if text:
                                doc.add_paragraph(text)
                                doc.add_page_break()

                    doc.save(output_docx)

                # Leitura do DOCX em memória
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
            st.success("Conversão concluída!")
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
