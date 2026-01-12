import streamlit as st
import pandas as pd
import re
import io

st.set_page_config(page_title="Conversor de Log Microsoft", layout="wide")

st.title("📊 Conversor de Relatórios (Precisão Total)")
st.markdown("Este app reconstrói registros fragmentados por tags `` e quebras de linha.")

def limpar_e_processar(texto_bruto):
    # 1. Remove as tags que aparecem no meio do texto
    # Corrigido o erro da barra invertida aqui
    texto = texto_bruto.replace('`', '')
    
    # 2. Une datas que foram quebradas em várias linhas
    # Isso procura por "dia de [quebra de linha] mês" e remove a quebra
    texto = re.sub(r'(\d{1,2}\s+de)\s*\n\s*(\w+)', r'\1 \2', texto)
    
    # 3. Padrão da data para separação (17 de dez de 2025 às 19:19)
    padrao_data = r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4}\s+às\s+\d{2}:\d{2})'
    
    # 4. Divide o texto em blocos baseados na data encontrada
    partes = re.split(padrao_data, texto)
    
    if partes and not partes[0].strip():
        partes.pop(0)
        
    registros = []
    
    # O split gera: [data, resto, data, resto...]
    for i in range(0, len(partes), 2):
        if i + 1 < len(partes):
            data_hora = partes[i].strip()
            # Limpa o conteúdo e remove linhas vazias
            bloco = partes[i+1].strip()
            linhas = [l.strip() for l in bloco.split('\n') if l.strip()]
            
            registros.append({
                'Data e Hora': data_hora,
                'Endereço IP': linhas[0] if len(linhas) > 0 else "",
                'Usuário':     linhas[1] if len(linhas) > 1 else "",
                'Serviço':     linhas[2] if len(linhas) > 2 else "",
                'Atividade':   linhas[3] if len(linhas) > 3 else "",
                'Detalhes':    " | ".join(linhas[4:]) if len(linhas) > 4 else ""
            })
            
    return pd.DataFrame(registros)

# Interface Streamlit
arquivo = st.file_uploader("Suba seu arquivo report.txt", type=['txt', 'csv'])

if arquivo:
    try:
        # Tenta ler o arquivo lidando com diferentes formatos de texto
        conteudo = arquivo.getvalue().decode("utf-8", errors="ignore")
        
        df = limpar_e_processar(conteudo)
        
        if not df.empty:
            st.success(f"✅ Processado! {len(df)} registros encontrados.")
            st.dataframe(df, use_container_width=True)
            
            # Preparar o Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Relatorio')
            
            st.download_button(
                label="📥 Baixar Planilha Excel",
                data=buffer.getvalue(),
                file_name="relatorio_organizado.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            st.warning("Nenhum registro foi identificado. Verifique o padrão das datas.")
            
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
