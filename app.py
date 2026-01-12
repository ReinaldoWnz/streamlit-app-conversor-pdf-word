def limpar_e_processar(texto_bruto):
    texto = texto_bruto.replace('`', '')

    padrao_data = r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4}\s+às\s+\d{2}:\d{2})'
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
