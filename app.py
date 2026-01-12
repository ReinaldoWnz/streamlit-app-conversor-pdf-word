import streamlit as st
import pandas as pd
import re
import io

st.set_page_config(page_title="Conversor de Log 407", layout="wide")

st.title("📊 Conversor de Relatórios - Alta Precisão")
st.markdown("Esta versão limpa interferências como `` e corrige datas quebradas entre linhas.")

def processar_logs_com_precisao(texto_bruto):
    # 1. Limpeza inicial: Remove marcações de fonte , , etc.
    texto_limpo = re.sub(r'\', '', texto_bruto)
    
    # 2. Define o padrão da data (Ex: 26 de dez de 2025 às 20:03)
    # Usamos parênteses para manter a data no resultado do split
    padrao_data = r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4}\s+às\s+\d{2}:\d{2})'
    
    # 3. Divide o texto usando a data como separador
    # O re.split com o padrão entre parênteses retorna [data1, resto1, data2, resto2...]
    partes = re.split(padrao_data, texto_limpo)
    
    # Remove a primeira parte se estiver vazia (antes da primeira data)
    if partes and not partes[0].strip():
        partes.pop(0)
        
    registros = []
    
    # 4. Agrupa os pares (Data, Conteúdo do Registro)
    for i in range(0, len(partes), 2):
        if i + 1 < len(partes):
            data_hora = partes[i].strip()
            conteudo = partes[i+1].strip()
            
            # Limpa as linhas dentro do conteúdo
            linhas_conteudo = [l.strip() for l in conteudo.split('\n') if l.strip()]
            
            registros.append({
                'Data e Hora': data_hora,
                'Endereço IP': linhas_conteudo[0] if len(linhas_conteudo) > 0 else "",
                'Usuário':     linhas_conteudo[1] if len(linhas_conteudo) > 1 else "",
                'Serviço':     linhas_conteudo[2] if len(linhas_conteudo) > 2 else "",
                'Atividade':   linhas_conteudo[3] if len(linhas_conteudo) > 3 else "",
                'Detalhes':    " | ".join(linhas_conteudo[4:]) if len(linhas_conteudo) > 4 else ""
            })
            
    return pd.DataFrame(registros)

arquivo_upload = st.file_uploader("Suba o arquivo report.txt", type=['txt', 'csv'])

if arquivo_upload is not None:
    try:
        # Lê o arquivo e tenta diferentes encodings
        bytes_data = arquivo_upload.getvalue()
        try:
            texto = bytes_data.decode("utf-8")
        except UnicodeDecodeError:
            texto = bytes_data.decode("iso-8859-1")
            
        df = processar_logs_com_precisao(texto)
        
        if not df.empty:
            st.success(f"✅ Sucesso! Foram encontrados {len(df)} registros.")
            
            # Visualização
            st.dataframe(df, use_container_width=True)
            
            # Download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Logs_Completos')
            
            st.download_button(
                label="📥 Baixar Planilha com Todos os Registros",
                data=buffer,
                file_name="relatorio_final.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            st.error("Nenhuma data encontrada. Verifique se o formato coincide com '17 de dez de 2025 às 19:19'")
            
    except Exception as e:
        st.error(f"Erro no processamento: {e}")
