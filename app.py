import streamlit as st
from pdf2docx import Converter
from io import BytesIO
import os
import traceback
import pypandoc

st.title("Conversor PDF para Word 📄➡️📝 (com fallback automático)")
st.write("Envie **um ou vários PDFs** — o app tentará manter a formatação, mas se falhar, converte o conteúdo bruto automaticamente.")

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

                # --- PRIMEIRA TENTATIVA: pdf2docx ---
                try:
                    cv = Converter(input_pdf)
                    cv.convert(output_docx, start=0, end=None)
                    cv.close()
                except Exception as e1:
                    st.warning(f"⚠️ {pdf.name} falhou com pdf2docx, tentando método alternativo...")
                    # --- SEGUNDA TENTATIVA: pypandoc (fallback) ---
                    try:
                        pypandoc.convert_text(
                            open(input_pdf, 'rb').read(),
                            'docx',
                            format='pdf',
                            outputfile=output_docx,
                            extra_args=['--standalone']
                        )
                    except Exception as e2:
                        raise Exception(f"pdf2docx e fallback falharam: {str(e2)}") from e2

                # Ler resultado em memória
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

        # Exibir resultados
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
