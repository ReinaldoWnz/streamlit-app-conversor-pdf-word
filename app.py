import streamlit as st
import pandas as pd
import re
import io

st.set_page_config(page_title="Conversor de Log Microsoft", layout="wide")

st.title("📊 Conversor de Relatórios (Precisão Total)")
st.markdown("Este app reconstrói registros fragmentados por tags `` e quebras de linha.")
def limpar_e_processar(texto_bruto):
    texto = texto_bruto.replace('`', '')

    padrao_data = r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4}\s+às[\s\xa0]*\d{1,2}:\d{2})'
    partes = re.split(padrao_data, texto)

    if partes and not partes[0].strip():
        partes.pop(0)

    registros = []

    for i in range(0, len(partes), 2):
        if i + 1 >= len(partes):
            continue

        data_hora = partes[i].strip()
        bloco = partes[i + 1].strip()

        linhas = [l.strip() for l in bloco.split('\n') if l.strip()]

        ip = linhas[0] if len(linhas) > 0 else ""
        usuario = linhas[1] if len(linhas) > 1 else ""
        servico = linhas[2] if len(linhas) > 2 else ""
        atividade = linhas[3] if len(linhas) > 3 else ""

        detalhes = " | ".join(linhas[4:]) if len(linhas) > 4 else ""

        registros.append({
            "Data e Hora": data_hora,
            "Endereço IP": ip,
            "Usuário": usuario,
            "Serviço": servico,
            "Atividade": atividade,
            "Detalhes": detalhes
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
