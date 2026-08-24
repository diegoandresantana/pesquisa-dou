@app.get("/api/atos")
def listar_atos(
    orgao: str = Query("IPEA", description="Sigla do órgão (padrão: IPEA) ou TODOS"),
    q: str = "",
    tipo: str = ""
):
    orgao_upper = orgao.upper()
    dados = []

    if os.path.exists("dados_dou_orgaos.json"):
        with open("dados_dou_orgaos.json", "r", encoding="utf-8") as f:
            base_completa = json.load(f)
            
            if orgao_upper == "TODOS":
                for lista in base_completa.values():
                    dados.extend(lista)
            else:
                dados = base_completa.get(orgao_upper, [])
    else:
        if orgao_upper == "TODOS":
            for sigla in ["IPEA", "IFMS", "ANPD", "MEC", "MCTI", "IBGE"]:
                dados.extend(coletar_atos(sigla, paginas=1))
        else:
            dados = coletar_atos(orgao_upper, paginas=1)

    if q:
        q_lower = q.lower()
        dados = [d for d in dados if q_lower in d["ato"].lower() or q_lower in d["resumo"].lower()]
    
    if tipo:
        dados = [d for d in dados if d["tipo"].lower() == tipo.lower()]

    return dados