"""
Módulo de busca no Diário Oficial da União (DOU) usando a API do Ro-dou.
Documentação da API: https://github.com/gestaogovbr/Ro-dou
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# URL base da API do Ro-dou (pode ser alterada para uma instância própria se necessário)
RO_DOU_API_URL = "https://ro-dou.dados.gov.br/api/search"

def buscar_atos_dou(
    orgao: str = "IPEA",
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    secao: str = "1",
    termo: Optional[str] = None,
    limite: int = 50
) -> List[Dict]:
    """
    Busca atos no DOU usando a API do Ro-dou.
    
    Args:
        orgao: Órgão de interesse (ex: 'IPEA', 'MINISTERIO DA SAUDE')
        data_inicio: Data de início no formato 'YYYY-MM-DD' (padrão: hoje)
        data_fim: Data de fim no formato 'YYYY-MM-DD' (padrão: hoje)
        secao: Seção do DOU (1, 2 ou 3) - 1=Atos Executivos, 2=Legislação, 3=Editais
        termo: Termo adicional para busca (opcional)
        limite: Quantidade máxima de resultados
    
    Returns:
        Lista de dicionários com os dados dos atos encontrados
    """
    
    # Define datas padrão (hoje) se não fornecidas
    if not data_inicio:
        data_inicio = datetime.now().strftime("%Y-%m-%d")
    if not data_fim:
        data_fim = data_inicio
    
    # Parâmetros da requisição
    params = {
        "q": f'orgao:"{orgao}"',
        "date_from": data_inicio,
        "date_to": data_fim,
        "section": secao,
        "page_size": limite,
        "field_list": "title,description,href,department,pubDate,section"
    }
    
    # Adiciona termo de busca se fornecido
    if termo:
        params["q"] = f'{params["q"]} AND ({termo})'
    
    try:
        print(f"🔍 Buscando no DOU: órgão={orgao}, período={data_inicio} a {data_fim}, seção={secao}")
        
        response = requests.get(RO_DOU_API_URL, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # A API retorna os resultados em 'results'
        resultados = data.get("results", [])
        
        print(f"✅ Encontrados {len(resultados)} atos no DOU")
        
        # Formata os resultados para o nosso padrão
        atos_formatados = []
        for item in resultados:
            ato = {
                "titulo": item.get("title", ""),
                "descricao": item.get("description", ""),
                "link": item.get("href", ""),
                "orgao": item.get("department", orgao),
                "data_publicacao": item.get("pubDate", ""),
                "secao": item.get("section", secao),
                "texto_completo": item.get("description", "")
            }
            atos_formatados.append(ato)
        
        return atos_formatados
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição à API do Ro-dou: {e}")
        return []
    except Exception as e:
        print(f"❌ Erro ao processar dados do DOU: {e}")
        return []


def buscar_portarias_nomeacao(
    orgao: str = "IPEA",
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    limite: int = 50
) -> List[Dict]:
    """
    Busca especificamente portarias de nomeação/designação no DOU.
    
    Args:
        orgao: Órgão de interesse
        data_inicio: Data de início (YYYY-MM-DD)
        data_fim: Data de fim (YYYY-MM-DD)
        limite: Quantidade máxima de resultados
    
    Returns:
        Lista de atos relacionados a nomeações
    """
    termos_nomeacao = "NOMEAÇÃO OR DESIGNAÇÃO OR PORTARIA"
    return buscar_atos_dou(
        orgao=orgao,
        data_inicio=data_inicio,
        data_fim=data_fim,
        termo=termos_nomeacao,
        limite=limite
    )


def buscar_exoneracoes(
    orgao: str = "IPEA",
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    limite: int = 50
) -> List[Dict]:
    """
    Busca especificamente exonerações/dispensas no DOU.
    
    Args:
        orgao: Órgão de interesse
        data_inicio: Data de início (YYYY-MM-DD)
        data_fim: Data de fim (YYYY-MM-DD)
        limite: Quantidade máxima de resultados
    
    Returns:
        Lista de atos relacionados a exonerações
    """
    termos_exoneracao = "EXONERAÇÃO OR DISPENSA OR EXONERAR OR DISPENSAR"
    return buscar_atos_dou(
        orgao=orgao,
        data_inicio=data_inicio,
        data_fim=data_fim,
        termo=termos_exoneracao,
        limite=limite
    )


if __name__ == "__main__":
    # Teste do módulo
    print("=" * 60)
    print("TESTE DO MÓDULO DE BUSCA NO DOU")
    print("=" * 60)
    
    # Teste 1: Busca geral
    print("\n📋 Teste 1: Busca geral de atos do IPEA (últimos 7 dias)")
    hoje = datetime.now()
    sete_dias_atras = (hoje - timedelta(days=7)).strftime("%Y-%m-%d")
    hoje_str = hoje.strftime("%Y-%m-%d")
    
    atos = buscar_atos_dou(
        orgao="IPEA",
        data_inicio=sete_dias_atras,
        data_fim=hoje_str,
        limite=10
    )
    
    if atos:
        print(f"\n✅ Sucesso! {len(atos)} atos encontrados:")
        for i, ato in enumerate(atos[:5], 1):  # Mostra apenas os 5 primeiros
            print(f"\n{i}. Título: {ato['titulo'][:80]}...")
            print(f"   Link: {ato['link']}")
            print(f"   Data: {ato['data_publicacao']}")
            print(f"   Seção: {ato['secao']}")
    else:
        print("\n⚠️ Nenhum ato encontrado neste período.")
    
    # Teste 2: Busca de nomeações
    print("\n\n📋 Teste 2: Busca de nomeações do IPEA")
    nomeacoes = buscar_portarias_nomeacao(
        orgao="IPEA",
        data_inicio=sete_dias_atras,
        data_fim=hoje_str,
        limite=5
    )
    
    if nomeacoes:
        print(f"\n✅ Sucesso! {len(nomeacoes)} nomeações encontradas:")
        for i, ato in enumerate(nomeacoes, 1):
            print(f"\n{i}. {ato['titulo'][:80]}...")
            print(f"   Link: {ato['link']}")
    else:
        print("\n⚠️ Nenhuma nomeação encontrada neste período.")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)
