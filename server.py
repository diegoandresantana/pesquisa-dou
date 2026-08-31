"""
Servidor Backend para o Portal de Atos do DOU
Backend completo com FastAPI para coleta e disponibilização de atos oficiais
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import requests
from bs4 import BeautifulSoup

# Importa o módulo de busca no DOU (Ro-dou API)
import dou_search

app = FastAPI(
    title="Portal de Atos DOU",
    description="API para consulta de atos oficiais do Diário Oficial da União - Seção 2",
    version="1.0.0"
)

# Configurar CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista de órgãos disponíveis
ORGANIZACOES = [
    {"sigla": "IPEA", "nome": "Instituto de Pesquisa Econômica Aplicada"},
    {"sigla": "IFMS", "nome": "Instituto Federal de Mato Grosso do Sul"},
    {"sigla": "ANPD", "nome": "Autoridade Nacional de Proteção de Dados"},
    {"sigla": "MEC", "nome": "Ministério da Educação"},
    {"sigla": "MCTI", "nome": "Ministério da Ciência, Tecnologia e Inovação"},
    {"sigla": "IBGE", "nome": "Instituto Brasileiro de Geografia e Estatística"},
    {"sigla": "INPE", "nome": "Instituto Nacional de Pesquisas Espaciais"},
    {"sigla": "CAPES", "nome": "Coordenação de Aperfeiçoamento de Pessoal de Nível Superior"},
    {"sigla": "CNPQ", "nome": "Conselho Nacional de Desenvolvimento Científico e Tecnológico"},
    {"sigla": "FINEP", "nome": "Financiadora de Estudos e Projetos"},
]

ARQUIVO_DADOS = "dados_dou_orgaos.json"


def coletar_atos(orgao: str, paginas: int = 3) -> List[Dict[str, Any]]:
    """
    Coleta atos do DOU para um órgão específico.
    Simula a coleta de dados (em produção, implementaria scraping real).
    """
    dados_coletados = []
    
    # URLs base para busca no DOU (exemplo genérico)
    base_url = "https://www.in.gov.br/web/dou/-/dou"
    
    # Mapeamento de tipos de ato
    tipos_ato = {
        "PORTARIA": "Portaria",
        "NOMEACAO": "Nomeação",
        "EXONERACAO": "Exoneração",
        "DESIGNACAO": "Designação",
        "DISPENSA": "Dispensa",
        "SUBSTITUICAO": "Substituição",
        "LOTACAO": "Lotação",
        "READAPTAÇÃO": "Readaptação",
        "REMOCAO": "Remoção",
        "REDISTRIBUICAO": "Redistribuição",
        "APOSENTADORIA": "Aposentadoria",
        "VACANCIA": "Vacância",
        "OUTROS": "Outros"
    }
    
    # Nomes fictícios para simulação
    nomes_servidores = [
        "João Silva Santos", "Maria Oliveira Costa", "Pedro Henrique Souza", 
        "Ana Paula Ferreira", "Carlos Eduardo Lima", "Juliana Mendes Rocha",
        "Roberto Alves Pereira", "Fernanda Carvalho Gomes", "Lucas Martins Barbosa",
        "Patricia Ribeiro Dias"
    ]
    
    cargos = [
        "Cargo em Comissão FCE-123", "Função Comissionada FCE-456", 
        "Diretor de Departamento", "Coordenador Geral", "Chefe de Divisão",
        "Assessor Técnico", "Analista Administrativo"
    ]
    
    diretorias = [
        "Diretoria de Planejamento", "Coordenação de Pesquisa", 
        "Departamento de Administração", "Divisão de Recursos Humanos",
        "Gerência de Tecnologia"
    ]
    
    # Gerar dados simulados para demonstração
    # Em produção, isso seria substituído por scraping real do site do DOU
    for i in range(paginas):
        data_base = datetime.now() - timedelta(days=i)
        data_str = data_base.strftime("%d/%m/%Y")
        
        # Simular alguns atos para cada órgão com dados estruturados
        atos_simulados = [
            {
                "orgao": orgao,
                "data": data_str,
                "tipo": "Nomeação",
                "ato": f"PORTARIA Nº {100 + i * 10 + 1}, de {data_str}",
                "resumo": f"Nomeia servidor {nomes_servidores[i % len(nomes_servidores)]} para {cargos[i % len(cargos)]} na {diretorias[i % len(diretorias)]}. Processo administrativo nº {2024000 + i}. Vigência a partir da publicação.",
                "link": f"https://www.in.gov.br/web/dou/-/dou-{orgao.lower()}-{data_base.strftime('%Y%m%d')}",
                "nome": nomes_servidores[i % len(nomes_servidores)],
                "cargo": cargos[i % len(cargos)],
                "fce": f"FCE-{100+i}",
                "diretoria": diretorias[i % len(diretorias)],
                "dtPortaria": data_str,
                "pubDOU": data_str,
                "vigencia": "Indeterminada"
            },
            {
                "orgao": orgao,
                "data": data_str,
                "tipo": "Exoneração",
                "ato": f"PORTARIA Nº {200 + i * 10 + 2}, de {data_str}",
                "resumo": f"Exonera servidor {nomes_servidores[(i+1) % len(nomes_servidores)]} do cargo de confiança na {diretorias[(i+1) % len(diretorias)]}. A pedido.",
                "link": f"https://www.in.gov.br/web/dou/-/dou-{orgao.lower()}-{data_base.strftime('%Y%m%d')}-2",
                "nome": nomes_servidores[(i+1) % len(nomes_servidores)],
                "cargo": cargos[(i+1) % len(cargos)],
                "fce": "-",
                "diretoria": diretorias[(i+1) % len(diretorias)],
                "dtPortaria": data_str,
                "pubDOU": data_str,
                "vigencia": "-"
            },
            {
                "orgao": orgao,
                "data": data_str,
                "tipo": "Substitição",
                "ato": f"PORTARIA Nº {300 + i * 10 + 3}, de {data_str}",
                "resumo": f"Designa servidor {nomes_servidores[(i+2) % len(nomes_servidores)]} para substituir titular em exercício na {diretorias[(i+2) % len(diretorias)]}. Período determinado de 30 dias. Responder temporariamente como substituto eventual.",
                "link": f"https://www.in.gov.br/web/dou/-/dou-{orgao.lower()}-{data_base.strftime('%Y%m%d')}-3",
                "nome": nomes_servidores[(i+2) % len(nomes_servidores)],
                "cargo": "Substituto Eventual",
                "fce": "FCE-789",
                "diretoria": diretorias[(i+2) % len(diretorias)],
                "dtPortaria": data_str,
                "pubDOU": data_str,
                "vigencia": "30 dias"
            },
            {
                "orgao": orgao,
                "data": data_str,
                "tipo": "Dispensa",
                "ato": f"PORTARIA Nº {400 + i * 10 + 4}, de {data_str}",
                "resumo": f"Dispensa servidor {nomes_servidores[(i+3) % len(nomes_servidores)]} da função de substituição na {diretorias[(i+3) % len(diretorias)]}. Fim do período de substituição.",
                "link": f"https://www.in.gov.br/web/dou/-/dou-{orgao.lower()}-{data_base.strftime('%Y%m%d')}-4",
                "nome": nomes_servidores[(i+3) % len(nomes_servidores)],
                "cargo": "Substituto",
                "fce": "-",
                "diretoria": diretorias[(i+3) % len(diretorias)],
                "dtPortaria": data_str,
                "pubDOU": data_str,
                "vigencia": "-"
            }
        ]
        
        dados_coletados.extend(atos_simulados)
    
    return dados_coletados


def carregar_ou_coletar_dados(orgao: str) -> List[Dict[str, Any]]:
    """
    Carrega dados do arquivo JSON ou coleta novos dados se não existirem.
    """
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            base_completa = json.load(f)
            
            if orgao.upper() == "TODOS":
                dados = []
                for lista in base_completa.values():
                    dados.extend(lista)
                return dados
            else:
                return base_completa.get(orgao.upper(), [])
    else:
        # Coletar dados se arquivo não existir
        if orgao.upper() == "TODOS":
            dados = []
            for organizacao in ORGANIZACOES:
                sigla = organizacao["sigla"]
                dados.extend(coletar_atos(sigla, paginas=2))
            return dados
        else:
            return coletar_atos(orgao.upper(), paginas=3)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve a interface web principal."""
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return {"message": "Portal de Atos DOU - Acesse /docs para documentação da API"}


@app.get("/api/organizacoes")
async def listar_organizacoes():
    """Retorna lista de todas as organizações disponíveis."""
    return ORGANIZACOES


@app.get("/api/atos")
async def listar_atos(
    orgao: str = Query("IPEA", description="Sigla do órgão (padrão: IPEA) ou TODOS"),
    q: str = "",
    tipo: str = ""
):
    """
    Lista atos do DOU filtrados por órgão, termo de busca e tipo.
    
    - **orgao**: Sigla do órgão (IPEA, MEC, etc.) ou 'TODOS' para todos os órgãos
    - **q**: Termo de busca para filtrar no texto dos atos
    - **tipo**: Tipo de ato (Nomeação, Exoneração, Substitição, etc.)
    """
    orgao_upper = orgao.upper()
    dados = carregar_ou_coletar_dados(orgao_upper)
    
    # Filtrar por termo de busca
    if q:
        q_lower = q.lower()
        dados = [
            d for d in dados 
            if q_lower in d["ato"].lower() or q_lower in d["resumo"].lower()
        ]
    
    # Filtrar por tipo
    if tipo:
        dados = [d for d in dados if d["tipo"].lower() == tipo.lower()]
    
    return dados


@app.get("/api/coletar")
async def forcar_coleta(
    orgao: str = Query("TODOS", description="Órgão para coletar ou TODOS")
):
    """
    Força a coleta de novos dados do DOU e salva no arquivo JSON.
    Útil para atualizar a base de dados manualmente.
    """
    orgao_upper = orgao.upper()
    
    if orgao_upper == "TODOS":
        dados_completos = {}
        for organizacao in ORGANIZACOES:
            sigla = organizacao["sigla"]
            dados_completos[sigla] = coletar_atos(sigla, paginas=5)
        
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(dados_completos, f, ensure_ascii=False, indent=2)
        
        total = sum(len(v) for v in dados_completos.values())
        return {
            "status": "sucesso",
            "mensagem": f"Dados coletados e salvos para {len(dados_completos)} organizações",
            "total_atos": total,
            "detalhes": {k: len(v) for k, v in dados_completos.items()}
        }
    else:
        dados = coletar_atos(orgao_upper, paginas=5)
        
        # Carregar existente ou criar novo
        if os.path.exists(ARQUIVO_DADOS):
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                base_completa = json.load(f)
        else:
            base_completa = {}
        
        base_completa[orgao_upper] = dados
        
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(base_completa, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "sucesso",
            "mensagem": f"Dados coletados e salvos para {orgao_upper}",
            "total_atos": len(dados)
        }


@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da API."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 Iniciando servidor do Portal de Atos DOU")
    print("=" * 60)
    print("📍 Acesse: http://127.0.0.1:8000")
    print("📚 Documentação API: http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
