import streamlit as st
from pdf2docx import Converter
from io import BytesIO
import os
import traceback

st.title("Conversor PDF para Word 📄➡️📝 (com formatação)")
st.write("Envie **um ou vários PDFs** e baixe os arquivos Word convertidos separadamente.")

# Permite múltiplos uploads
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
                # Salvar PDF temporariamente
                with open(input_pdf, "wb") as f:
                    f.write(pdf.read())

                # Converter PDF -> DOCX
                cv = Converter(input_pdf)
                cv.convert(output_docx, start=0, end=None)
                cv.close()

                # Ler DOCX em memória para download
                with open(output_docx, "rb") as f:
                    buffer = BytesIO(f.read())

                resultados.append((nome_base, buffer))

            except Exception as e:
                erros.append(f"❌ Erro ao converter {pdf.name}: {str(e)}")
                traceback.print_exc()  # Mostra no log do Streamlit Cloud

            finally:
                # Limpa arquivos temporários (se existirem)
                if os.path.exists(input_pdf):
                    os.remove(input_pdf)
                if os.path.exists(output_docx):
                    os.remove(output_docx)

        # Mostra resultados
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
