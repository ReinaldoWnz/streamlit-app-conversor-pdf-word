import streamlit as st
import pandas as pd
import re
import io

st.set_page_config(page_title="Conversor de Log Full", layout="wide")

st.title("📊 Conversor de Relatórios (Processamento Completo)")
st.markdown("Este app identifica automaticamente novos registros sempre que uma linha começa com uma data.")

def processar_texto_robusto(conteudo_texto):
    # Divide o texto em linhas e limpa espaços extras
    linhas = [l.strip() for l in conteudo_texto.split('\n') if l.strip()]
    
    # REGEX MELHORADA: 
    # \d{1,2} -> dia (1 ou 2 dígitos)
    # \s+de\s+ -> " de " com qualquer espaço
    # \w+ -> mês de qualquer tamanho (jan, dezembro, etc)
    # às -> aceita a crase
    padrao_data = r'^\d{1,2}\s+de\s+\w+\s+de\s+\d{4}\s+às\s+\d{2}:\d{2}'
    
    registros = []
    bloco_atual = []

    for linha in linhas:
        # Verifica se a linha é o início de um novo bloco (Data)
        if re.match(padrao_data, linha, re.IGNORECASE):
            if bloco_atual:
                registros.append(mapear_colunas(bloco_atual))
            bloco_atual = [linha]
        else:
            bloco_atual.append(linha)

    # Não esquecer o último bloco do arquivo
    if bloco_atual:
        registros.append(mapear_colunas(bloco_atual))
        
    return pd.DataFrame(registros)

def mapear_colunas(linhas):
    """
    Distribui as linhas capturadas. Como os blocos variam, 
    pegamos as 5 primeiras fixas e o restante vira 'Detalhes'.
    """
    # Se o bloco for muito curto (erro de cópia), preenche com vazio
    info = {
        'Data e Hora': linhas[0] if len(linhas) > 0 else "",
        'Endereço IP': linhas[1] if len(linhas) > 1 else "",
        'Usuário':     linhas[2] if len(linhas) > 2 else "",
        'Serviço':     linhas[3] if len(linhas) > 3 else "",
        'Atividade':   linhas[4] if len(linhas) > 4 else "",
        # Aqui capturamos TUDO o que sobrar (linha 5, 6, 7...)
        'Detalhes Extra': " | ".join(linhas[5:]) if len(linhas) > 5 else ""
    }
    return info

arquivo_upload = st.file_uploader("Arraste seu arquivo .txt aqui", type=['txt', 'csv'])

if arquivo_upload is not None:
    try:
        # Tenta ler em UTF-8, se falhar tenta ISO-8859-1 (comum em logs br)
        bytes_data = arquivo_upload.getvalue()
        try:
            conteudo = bytes_data.decode("utf-8")
        except UnicodeDecodeError:
            conteudo = bytes_data.decode("iso-8859-1")
            
        df = processar_texto_robusto(conteudo)
        
        if not df.empty:
            st.success(f"✅ Sucesso! Foram processados {len(df)} registros.")
            
            # Filtro rápido para conferência
            st.dataframe(df, use_container_width=True)
            
            # Botão de Download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Logs')
            
            st.download_button(
                label="📥 Baixar Planilha Completa",
                data=buffer,
                file_name="relatorio_completo.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            st.error("A Regex não encontrou datas no início das linhas. Verifique o formato do arquivo.")
            
    except Exception as e:
        st.error(f"Erro ao processar: {e}")
