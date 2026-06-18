"""
Funções auxiliares para o sistema de humanização de texto.
"""

import json
import os
import re
from typing import List, Dict


def load_json_data(filename: str) -> dict:
    """
    Carrega dados de ficheiros JSON em data/
    
    Args:
        filename: Nome do ficheiro JSON (ex: 'ai_markers.json')
    
    Returns:
        Dicionário com os dados carregados
    
    Raises:
        FileNotFoundError: Se o ficheiro não existir
        json.JSONDecodeError: Se o JSON for inválido
    """
    # Obtém o diretório base do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = os.path.join(base_dir, 'data', filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def detect_nominalizations(text: str) -> List[str]:
    """
    Deteta palavras terminadas em sufixos de nominalização.
    
    Nominalização é o processo de transformar verbos/adjetivos em substantivos abstratos,
    comum em texto formal e IA (ex: "implementar" → "implementação").
    
    Sufixos procurados: -ção, -são, -mento, -ância, -ência, -ismo, -eza, -ura, -idade
    
    Args:
        text: Texto a analisar
    
    Returns:
        Lista de nominalizações encontradas (palavras únicas, lowercase)
    
    Examples:
        >>> detect_nominalizations("A implementação da avaliação foi complexa")
        ['implementação', 'avaliação']
    """
    # Pattern para capturar palavras com sufixos de nominalização
    pattern = r'\b\w+(?:ção|são|mento|ância|ência|ismo|eza|ura|idade)\b'
    
    # Encontra todas as ocorrências (case-insensitive)
    matches = re.findall(pattern, text.lower())
    
    # Remove duplicados mantendo ordem
    seen = set()
    unique_matches = []
    for match in matches:
        if match not in seen:
            seen.add(match)
            unique_matches.append(match)
    
    return unique_matches


def detect_passive_voice(doc) -> int:
    """
    Conta construções de voz passiva (auxiliar "ser" + particípio).
    
    A voz passiva é mais comum em texto formal e gerado por IA.
    Exemplo: "O relatório foi elaborado" (passiva) vs "Elaborámos o relatório" (ativa)
    
    Args:
        doc: Objeto spaCy Doc processado
    
    Returns:
        Número de construções passivas encontradas
    
    Notes:
        - Procura o padrão: verbo "ser" (auxiliar) + verbo no particípio
        - Usa análise morfológica do spaCy (POS tags e VerbForm)
    """
    count = 0
    
    for token in doc:
        # Verifica se é o auxiliar "ser" (qualquer forma: é, foi, era, seria, etc.)
        if token.lemma_ == 'ser' and token.pos_ == 'AUX':
            # Procura particípio nos filhos sintáticos
            for child in token.children:
                if child.pos_ == 'VERB':
                    # Verifica se é particípio (VerbForm=Part)
                    verb_form = child.morph.get('VerbForm')
                    if verb_form and 'Part' in verb_form:
                        count += 1
                        break  # Só conta uma vez por construção
    
    return count


def calculate_type_token_ratio(tokens: List[str]) -> float:
    """
    Calcula Type-Token Ratio (TTR): diversidade lexical.
    
    TTR = número de palavras únicas / número total de palavras
    Valores mais altos indicam maior diversidade vocabular.
    
    Args:
        tokens: Lista de tokens (palavras)
    
    Returns:
        TTR entre 0 e 1
    
    Examples:
        >>> calculate_type_token_ratio(['o', 'rato', 'roeu', 'o', 'rato'])
        0.6  # 3 palavras únicas / 5 palavras totais
    """
    if not tokens:
        return 0.0
    
    unique_tokens = set(tokens)
    return len(unique_tokens) / len(tokens)


def calculate_mtld(tokens: List[str], threshold: float = 0.72) -> float:
    """
    Calcula MTLD (Measure of Textual Lexical Diversity) - aproximação simplificada.
    
    MTLD mede diversidade lexical de forma mais robusta que TTR,
    sendo menos afetado pelo comprimento do texto.
    
    Args:
        tokens: Lista de tokens
        threshold: Threshold de TTR (padrão 0.72)
    
    Returns:
        Score MTLD (valores mais altos = maior diversidade)
    
    Notes:
        Esta é uma implementação simplificada do algoritmo MTLD completo.
    """
    if len(tokens) < 10:
        return 0.0
    
    def calculate_factor_length(token_list):
        """Calcula comprimento do fator até TTR cair abaixo do threshold"""
        ttr = 1.0
        types = set()
        
        for i, token in enumerate(token_list, 1):
            types.add(token)
            ttr = len(types) / i
            
            if ttr < threshold:
                return i
        
        return len(token_list)
    
    # Calcula MTLD em ambas as direções (forward e backward)
    forward_mtld = len(tokens) / max(1, calculate_factor_length(tokens))
    backward_mtld = len(tokens) / max(1, calculate_factor_length(tokens[::-1]))
    
    # Retorna média das duas direções
    return (forward_mtld + backward_mtld) / 2


def count_repeated_words(tokens: List[str], min_count: int = 3) -> Dict[str, int]:
    """
    Identifica palavras repetidas mais de N vezes.
    
    Args:
        tokens: Lista de tokens (lowercase)
        min_count: Número mínimo de ocorrências para considerar repetida
    
    Returns:
        Dicionário {palavra: número_ocorrências} para palavras repetidas
    
    Examples:
        >>> count_repeated_words(['o', 'rato', 'roeu', 'o', 'rato', 'o'], min_count=2)
        {'o': 3, 'rato': 2}
    """
    from collections import Counter
    
    word_counts = Counter(tokens)
    
    # Filtra palavras com contagem >= min_count
    repeated = {word: count for word, count in word_counts.items() 
                if count >= min_count}
    
    return repeated


def detect_first_person_pronouns(text: str) -> int:
    """
    Conta pronomes de primeira pessoa.
    
    Args:
        text: Texto a analisar
    
    Returns:
        Número de pronomes de 1ª pessoa encontrados
    """
    pronouns = [
        r'\beu\b', r'\bme\b', r'\bmim\b', r'\bcomigo\b',
        r'\bmeu\b', r'\bminha\b', r'\bmeus\b', r'\bminhas\b',
        r'\bn[óo]s\b', r'\bnos\b', r'\bconosco\b',
        r'\bnosso\b', r'\bnossa\b', r'\bnossos\b', r'\bnossas\b'
    ]
    
    count = 0
    text_lower = text.lower()
    
    for pronoun_pattern in pronouns:
        count += len(re.findall(pronoun_pattern, text_lower))
    
    return count


def detect_hedging_terms(text: str, hedging_list: List[str]) -> int:
    """
    Conta termos de hedging (cautela/incerteza) no texto.
    
    Args:
        text: Texto a analisar
        hedging_list: Lista de termos de hedging a procurar
    
    Returns:
        Número de termos de hedging encontrados
    """
    count = 0
    text_lower = text.lower()
    
    for term in hedging_list:
        # Usa word boundaries para evitar matches parciais
        pattern = r'\b' + re.escape(term) + r'\b'
        count += len(re.findall(pattern, text_lower))
    
    return count


def detect_ai_markers(text: str, markers_list: List[str]) -> List[str]:
    """
    Identifica marcadores/expressões típicas de IA no texto.
    
    Args:
        text: Texto a analisar
        markers_list: Lista de expressões-fórmula típicas de IA
    
    Returns:
        Lista de marcadores encontrados
    """
    found_markers = []
    text_lower = text.lower()
    
    for marker in markers_list:
        if marker.lower() in text_lower:
            found_markers.append(marker)
    
    return found_markers


def detect_formulaic_intro(text: str) -> bool:
    """
    Verifica se o texto começa com introdução formulaica típica de IA.
    
    Args:
        text: Texto a analisar
    
    Returns:
        True se tiver introdução formulaica
    """
    formulaic_patterns = [
        r'^neste\s+(texto|artigo|ensaio)',
        r'^este\s+(texto|artigo|ensaio)\s+(vai|irá|pretende)',
        r'^[éeÉE]\s+importante\s+(notar|salientar|referir)',
        r'^[éeÉE]\s+fundamental',
        r'^vamos\s+(explorar|analisar|examinar)',
        r'^iremos\s+(explorar|analisar|examinar)'
    ]
    
    text_start = text[:200].lower()  # Analisa apenas os primeiros 200 caracteres
    
    for pattern in formulaic_patterns:
        if re.search(pattern, text_start):
            return True
    
    return False


def detect_formulaic_conclusion(text: str) -> bool:
    """
    Verifica se o texto termina com conclusão formulaica típica de IA.
    
    Args:
        text: Texto a analisar
    
    Returns:
        True se tiver conclusão formulaica
    """
    formulaic_patterns = [
        r'em\s+(suma|conclus[ãa]o|s[íi]ntese)',
        r'conclui-se\s+que',
        r'concluindo',
        r'para\s+concluir',
        r'em\s+jeito\s+de\s+conclus[ãa]o'
    ]
    
    text_end = text[-200:].lower()  # Analisa apenas os últimos 200 caracteres
    
    for pattern in formulaic_patterns:
        if re.search(pattern, text_end):
            return True
    
    return False


def count_transition_markers(text: str) -> int:
    """
    Conta marcadores de transição típicos de estruturas académicas.
    
    Args:
        text: Texto a analisar
    
    Returns:
        Número de marcadores de transição
    """
    transition_patterns = [
        r'\bal[ée]m\s+disso\b',
        r'\bpor\s+outro\s+lado\b',
        r'\bem\s+primeiro\s+lugar\b',
        r'\bem\s+segundo\s+lugar\b',
        r'\bem\s+terceiro\s+lugar\b',
        r'\bprimeiramente\b',
        r'\bsegundamente\b',
        r'\bfinalmente\b',
        r'\bpor\s+[úu]ltimo\b'
    ]
    
    count = 0
    text_lower = text.lower()
    
    for pattern in transition_patterns:
        count += len(re.findall(pattern, text_lower))
    
    return count
