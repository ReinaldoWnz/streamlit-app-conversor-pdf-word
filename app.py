import streamlit as st
import pandas as pd
import re
import io

# Configuração da página
st.set_page_config(page_title="Conversor de Relatórios Microsoft", layout="wide")

st.title("📊 Conversor de Relatórios (Log para Tabela)")
st.markdown("""
Esta ferramenta transforma relatórios de texto brutos em uma tabela organizada. 
**A separação é feita automaticamente sempre que uma nova data é detectada.**
""")

def processar_texto(conteudo_texto):
    # Divide o texto em linhas e remove linhas vazias
    linhas = [l.strip() for l in conteudo_texto.split('\n') if l.strip()]
    
    # Padrão Regex para identificar a data (Ex: 26 de dez de 2025 às 20:03)
    padrao_data = r'^\d{1,2} de \w{3} de \d{4} às \d{2}:\d{2}'
    
    registros = []
    bloco_atual = []

    for linha in linhas:
        # Se a linha for uma data, fecha o bloco anterior e inicia um novo
        if re.match(padrao_data, linha):
            if bloco_atual:
                registros.append(mapear_colunas(bloco_atual))
            bloco_atual = [linha]
        else:
            bloco_atual.append(linha)

    # Adiciona o último bloco
    if bloco_atual:
        registros.append(mapear_colunas(bloco_atual))
        
    return pd.DataFrame(registros)

def mapear_colunas(linhas):
    """Organiza as linhas capturadas em colunas"""
    return {
        'Data e Hora': linhas[0] if len(linhas) > 0 else "",
        'Endereço IP': linhas[1] if len(linhas) > 1 else "",
        'Usuário':     linhas[2] if len(linhas) > 2 else "",
        'Serviço':     linhas[3] if len(linhas) > 3 else "",
        'Atividade':   linhas[4] if len(linhas) > 4 else "",
        'Detalhes':    " | ".join(linhas[5:]) if len(linhas) > 5 else ""
    }

# Upload do arquivo
arquivo_upload = st.file_uploader("Escolha o arquivo de texto (.txt ou .csv)", type=['txt', 'csv'])

if arquivo_upload is not None:
    # Ler o conteúdo do arquivo enviado
    stringio = io.StringIO(arquivo_upload.getvalue().decode("utf-8"))
    conteudo = stringio.read()
    
    # Processar
    df = processar_texto(conteudo)
    
    if not df.empty:
        st.success(f"Encontrados {len(df)} registros!")
        
        # Mostrar prévia da tabela
        st.dataframe(df, use_container_width=True)
        
        # Preparar download para Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Relatorio')
            
        st.download_button(
            label="📥 Baixar em Excel (.xlsx)",
            data=buffer,
            file_name="relatorio_processado.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.warning("Nenhum registro encontrado no formato esperado.")

st.info("💡 Dica: O app identifica o início de cada registro pela linha da data.")
