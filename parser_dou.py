"""
Parser para converter dados brutos da API do Ro-dou
para o formato estruturado AtoDOU usado pelo sistema.
"""
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


def extrair_nome(texto: str) -> Optional[str]:
    """Extrai nome de pessoa do texto do ato."""
    # Padrões comuns: "nomear FULANO DE TAL", "designar BELTRANO"
    padroes = [
        r'(?:nomear|designar|contratar)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,})',  # Nome com 3+ palavras
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            nome = match.group(1).strip()
            # Filtra nomes muito curtos ou genéricos
            if len(nome) > 5 and 'PORTARIA' not in nome:
                return nome
    return None


def extrair_cargo(texto: str) -> Optional[str]:
    """Extrai cargo/função do texto do ato."""
    cargos_comuns = [
        r'(Diretor[a-z]*|Chefe\s+(?:de\s+)?Gabinete|Coordenador[a-z]*|Gerente|Supervisor[a-z]*)',
        r'(Assessor[a-z]*|Consultor[a-z]*|Analista|Técnico[a-z]*)',
        r'(Presidente|Vice[- ]?Presidente|Secretário[a-z]*|Subsecretário[a-z]*)',
        r'(FCE|DAS|CD|SG)[-\s]?\d+',
    ]
    
    for padrao in cargos_comuns:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    # Se não encontrar cargo específico, tenta pegar após "para"
    match = re.search(r'para\s+(exercer|atuar como)?\s*([\w\s]+?)(?:\.|$)', texto, re.IGNORECASE)
    if match:
        return match.group(2).strip()[:50]  # Limita tamanho
    
    return None


def extrair_fce(texto: str) -> Optional[str]:
    """Extrai código FCE/DAS/CD do texto."""
    padrao = r'\b(FCE|DAS|CD|SG)[-\s]?(\d+[A-Z]?)\b'
    match = re.search(padrao, texto, re.IGNORECASE)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return None


def extrair_sigla(texto: str) -> Optional[str]:
    """Extrai sigla da diretoria/unidade."""
    # Procura por siglas entre parênteses ou após "da"
    padroes = [
        r'\(([A-Z]{2,6})\)',  # Sigla entre parênteses
        r'(?:da|do)\s+([A-Z]{2,6})(?:\s|$)',  # Sigla após "da/do"
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            sigla = match.group(1)
            if sigla not in ['DOU', 'IN', 'PORTARIA', 'ATO']:
                return sigla
    return None


def extrair_diretoria(texto: str) -> Optional[str]:
    """Extrai nome da diretoria/unidade organizacional."""
    # Procura por padrões de diretorias
    padroes = [
        r'(Diretoria\s+(?:de|da|do)\s+[\w\s]+?)(?:\.|;|,|$)',
        r'(Coordenação\s+(?:de|da|do)\s+[\w\s]+?)(?:\.|;|,|$)',
        r'(Gerência\s+(?:de|da|do)\s+[\w\s]+?)(?:\.|;|,|$)',
        r'(Departamento\s+(?:de|da|do)\s+[\w\s]+?)(?:\.|;|,|$)',
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return match.group(1).strip()[:80]  # Limita tamanho
    
    return None


def classificar_tipo_ato(texto: str) -> str:
    """Classifica o tipo de ato baseado no conteúdo do texto."""
    texto_upper = texto.upper()
    
    if any(p in texto_upper for p in ['NOMEAR', 'NOMEAÇÃO']):
        return 'Nomeação'
    elif any(p in texto_upper for p in ['EXONERAR', 'EXONERAÇÃO']):
        return 'Exoneração'
    elif any(p in texto_upper for p in ['DESIGNAR', 'DESIGNAÇÃO']):
        return 'Designação'
    elif any(p in texto_upper for p in ['DISPENSAR', 'DISPENSA']):
        return 'Dispensa'
    elif any(p in texto_upper for p in ['SUBSTITUIR', 'SUBSTITUTO', 'SUBSTITUIÇÃO']):
        if 'EVENTUAL' in texto_upper:
            return 'Substituto eventual'
        return 'Substituição'
    elif any(p in texto_upper for p in ['RESPONDER', 'ACUMULAR']):
        return 'Responder (temp.)'
    elif any(p in texto_upper for p in ['PRORROGAR', 'PRORROGAÇÃO']):
        return 'Prorrogação'
    else:
        return 'Outros'


def extrair_vigencia(texto: str) -> Optional[str]:
    """Tenta extrair data de vigência do texto."""
    # Padrões de data
    padroes_data = [
        r'(\d{1,2}/\d{1,2}/\d{4})',
        r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
    ]
    
    datas = []
    for padrao in padroes_data:
        matches = re.findall(padrao, texto, re.IGNORECASE)
        datas.extend(matches)
    
    if datas:
        # Retorna a última data encontrada (provável vigência)
        return datas[-1] if len(datas) == 1 else f"{datas[0]} a {datas[-1]}"
    
    return None


def parsear_atos_ro_dou(dados_brutos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Converte lista de atos brutos do Ro-dou para formato estruturado.
    
    Args:
        dados_brutos: Lista de dicionários com campos 'title', 'description', 'link', etc.
    
    Returns:
        Lista de dicionários no formato AtoDOU
    """
    atos_processados = []
    
    for item in dados_brutos:
        try:
            titulo = item.get('title', '')
            descricao = item.get('description', '')
            link = item.get('url', item.get('link', ''))
            orgao = item.get('orgao', 'Desconhecido')
            data_pub = item.get('date', item.get('pubDate', ''))
            secao = item.get('section', '')
            
            # Combina título e descrição para análise
            texto_completo = f"{titulo} {descricao}"
            
            # Extrai informações estruturadas
            nome = extrair_nome(texto_completo)
            cargo = extrair_cargo(texto_completo)
            fce = extrair_fce(texto_completo)
            sigla = extrair_sigla(texto_completo)
            diretoria = extrair_diretoria(texto_completo)
            tipo_ato = classificar_tipo_ato(texto_completo)
            vigencia = extrair_vigencia(texto_completo)
            
            # Monta objeto estruturado
            ato_estruturado = {
                'orgao': orgao,
                'data': data_pub,
                'tipo': tipo_ato,
                'ato': titulo[:100] if titulo else 'Sem título',
                'resumo': descricao[:200] if descricao else titulo,
                'link': link,
                'nome': nome or '',
                'cargo': cargo or '',
                'fce': fce or '',
                'sigla': sigla or '',
                'diretoria': diretoria or '',
                'dtPortaria': data_pub.split('T')[0] if 'T' in str(data_pub) else data_pub,
                'pubDOU': data_pub.split('T')[0] if 'T' in str(data_pub) else data_pub,
                'vigencia': vigencia or '',
            }
            
            atos_processados.append(ato_estruturado)
            
        except Exception as e:
            print(f"Erro ao processar ato: {str(e)}")
            continue
    
    print(f"✅ Parser: {len(atos_processados)} atos processados com sucesso.")
    return atos_processados
