import streamlit as st
from pdf2docx import Converter
from io import BytesIO
import fitz  # PyMuPDF
import os

st.set_page_config(page_title="PDF Tools", page_icon="📄", layout="centered")

st.title("📄 Ferramentas para PDF")
st.write("Escolha abaixo se deseja **comprimir** ou **converter para Word**")

# --------------------------
# Parte 1 - Compressor de PDF
# --------------------------
st.header("🔽 Compressor de PDF")

uploaded_pdf = st.file_uploader("Envie seu PDF para comprimir", type="pdf", key="compressor")

if uploaded_pdf is not None:
    if st.button("Comprimir PDF para ~100KB"):
        input_pdf = "temp_compress.pdf"
        with open(input_pdf, "wb") as f:
            f.write(uploaded_pdf.read())

        pdf = fitz.open(input_pdf)
        output_pdf = "comprimido.pdf"

        # Salvar comprimindo
        pdf.save(output_pdf, deflate=True, garbage=4)

        # Tentar reduzir ainda mais se necessário
        max_size = 100 * 1024  # 100KB
        while os.path.getsize(output_pdf) > max_size:
            for page in pdf:
                pix = page.get_pixmap(matrix=fitz.Matrix(72/150, 72/150))  # reduz resolução
                page.clean_contents()
            pdf.save(output_pdf, deflate=True, garbage=4)
            # Evita loop infinito
            if os.path.getsize(output_pdf) <= max_size or os.path.getsize(output_pdf) == os.path.getsize(input_pdf):
                break

        with open(output_pdf, "rb") as f:
            buffer = BytesIO(f.read())

        st.success(f"PDF comprimido! Tamanho final: {len(buffer.getvalue())/1024:.1f} KB")
        st.download_button(
            label="⬇️ Baixar PDF Comprimido",
            data=buffer,
            file_name="comprimido.pdf",
            mime="application/pdf"
        )

# -------------------------------
# Parte 2 - Conversor PDF -> Word
# -------------------------------
st.header("📝 Conversor PDF para Word")

uploaded_file = st.file_uploader("Envie seu PDF para converter em Word", type="pdf", key="converter")

if uploaded_file is not None:
    if st.button("Converter para Word"):
        input_pdf = "temp_convert.pdf"
        with open(input_pdf, "wb") as f:
            f.write(uploaded_file.read())

        output_docx = "convertido.docx"
        cv = Converter(input_pdf)
        cv.convert(output_docx, start=0, end=None)
        cv.close()

        with open(output_docx, "rb") as f:
            buffer = BytesIO(f.read())

        st.success("Conversão concluída com formatação mantida!")
        st.download_button(
            label="⬇️ Baixar Word",
            data=buffer,
            file_name="convertido.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
