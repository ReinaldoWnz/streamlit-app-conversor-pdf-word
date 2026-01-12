import streamlit as st
import pandas as pd
import re
import io

st.set_page_config(page_title="Conversor de Log Premium", layout="wide")

st.title("📊 Conversor de Relatórios (Correção de Datas Fragmentadas)")

def processar_logs_limpos(texto_bruto):
    # 1. REMOVE as tags que quebram o texto 
    texto = re.sub(r'\', '', texto_bruto)
    
    # 2. CONSERTA datas que foram divididas por quebra de linha 
    # Exemplo: transforma "26 de\ndez" em "26 de dez"
    texto = re.sub(r'(\d{1,2}\s+de)\s*\n\s*(\w+)', r'\1 \2', texto)
    
    # 3. Define o padrão de data (17 de dez de 2025 às 19:19) [cite: 1, 10]
    padrao_data = r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4}\s+às\s+\d{2}:\d{2})'
    
    # 4. Divide o documento inteiro usando a data como separador único
    partes = re.split(padrao_data, texto)
    
    if partes and not partes[0].strip():
        partes.pop(0)
        
    registros = []
    
    # O split retorna [data, conteudo, data, conteudo...]
    for i in range(0, len(partes), 2):
        if i + 1 < len(partes):
            data_hora = partes[i].strip()
            # Limpa quebras de linha extras dentro do conteúdo do registro
            conteudo = partes[i+1].strip()
            linhas = [l.strip() for l in conteudo.split('\n') if l.strip()]
            
            registros.append({
                'Data e Hora': data_hora,
                'Endereço IP': linhas[0] if len(linhas) > 0 else "",
                'Usuário':     linhas[1] if len(linhas) > 1 else "",
                'Serviço':     linhas[2] if len(linhas) > 2 else "",
                'Atividade':   linhas[3] if len(linhas) > 3 else "",
                'Detalhes':    " | ".join(linhas[4:]) if len(linhas) > 4 else ""
            })
            
    return pd.DataFrame(registros)

arquivo_upload = st.file_uploader("Arraste o arquivo report.txt", type=['txt', 'csv'])

if arquivo_upload is not None:
    try:
        bytes_data = arquivo_upload.getvalue()
        try:
            texto_bruto = bytes_data.decode("utf-8")
        except:
            texto_bruto = bytes_data.decode("iso-8859-1")
            
        df = processar_logs_limpos(texto_bruto)
        
        if not df.empty:
            st.success(f"✅ Foram processados {len(df)} registros com sucesso!")
            st.dataframe(df, use_container_width=True)
            
            # Gerar Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Logs')
            
            st.download_button(
                label="📥 Baixar Excel Completo",
                data=output.getvalue(),
                file_name="relatorio_finalizado.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            st.error("Não foi possível identificar registros. Verifique o arquivo.")
    except Exception as e:
        st.error(f"Erro crítico: {e}")
