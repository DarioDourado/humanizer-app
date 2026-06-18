"""
Analisador linguístico ULTRA-RIGOROSO para detecção de padrões de texto gerado por IA.

Este módulo implementa a classe TextAnalyzer que realiza análise multidimensional
de texto usando spaCy, calculando métricas lexicais, sintáticas, de estilo e estrutura.

VERSÃO OPTIMIZADA - Critérios muito mais apertados para aproximar resultados do GPTZero
"""

import spacy
import statistics
import re
from collections import Counter
from typing import Dict, List, Tuple
from .utils import (
    load_json_data,
    detect_nominalizations,
    detect_passive_voice,
    calculate_type_token_ratio,
    calculate_mtld,
    count_repeated_words,
    detect_first_person_pronouns,
    detect_hedging_terms,
    detect_ai_markers,
    detect_formulaic_intro,
    detect_formulaic_conclusion,
    count_transition_markers
)


class TextAnalyzer:
    """
    Analisador linguístico ULTRA-RIGOROSO que diagnostica texto e atribui score de humanização.
    
    O score vai de 0-100 onde:
    - 0-30: Muito claramente IA
    - 31-50: Provavelmente IA
    - 51-70: Ambíguo / Melhorado mas ainda com padrões IA
    - 71-90: Provavelmente humano
    - 91-100: Muito provavelmente humano
    
    MUDANÇAS vs VERSÃO ANTERIOR:
    - Thresholds muito mais apertados
    - Pesos rebalanceados (mais peso em métricas críticas)
    - Novas métricas adicionadas (pontuação sofisticada, imperfeições)
    - Sistema de penalizações mais severo
    
    Attributes:
        nlp: Pipeline spaCy carregado
        ai_markers: Lista de expressões-fórmula típicas de IA
        hedging_terms: Lista de termos de cautela/hedging
    """
    
    def __init__(self, model: str = "pt_core_news_lg"):
        """
        Inicializa o analisador com modelo spaCy.
        
        Args:
            model: Nome do modelo spaCy a carregar (padrão: pt_core_news_lg)
        
        Raises:
            OSError: Se o modelo spaCy não estiver instalado
        """
        try:
            self.nlp = spacy.load(model)
        except OSError:
            raise OSError(
                f"Modelo spaCy '{model}' não encontrado. "
                f"Instale com: python -m spacy download {model}"
            )
        
        # Carrega dados de referência
        ai_markers_data = load_json_data('ai_markers.json')
        hedging_data = load_json_data('hedging_terms.json')
        
        self.ai_markers = ai_markers_data['markers']
        self.hedging_terms = hedging_data['terms']
    
    def analyze(self, text: str) -> Dict:
        """
        Análise completa do texto com todas as métricas.
        
        Args:
            text: Texto a analisar
        
        Returns:
            Dicionário com estrutura:
            {
                'lexical': {...},      # Métricas lexicais
                'syntactic': {...},    # Métricas sintáticas
                'style': {...},        # Métricas de estilo
                'structure': {...},    # Métricas de estrutura
                'score': int,          # Score global 0-100
                'score_breakdown': {...}  # Detalhamento do score
            }
        """
        # Processa texto com spaCy
        doc = self.nlp(text)
        
        # Calcula cada categoria de métricas
        lexical = self._analyze_lexical(text, doc)
        syntactic = self._analyze_syntactic(doc, text)  # Passa text também
        style = self._analyze_style(text, doc)
        structure = self._analyze_structure(text)
        
        # Calcula score global
        score_data = self._calculate_ai_score({
            'lexical': lexical,
            'syntactic': syntactic,
            'style': style,
            'structure': structure
        }, text)
        
        return {
            'lexical': lexical,
            'syntactic': syntactic,
            'style': style,
            'structure': structure,
            'score': score_data['final_score'],
            'score_breakdown': score_data
        }
    
    def _analyze_lexical(self, text: str, doc) -> Dict:
        """
        Análise de métricas lexicais (vocabulário e diversidade).
        
        Args:
            text: Texto original
            doc: spaCy Doc object
        
        Returns:
            Dicionário com métricas lexicais
        """
        # Extrai tokens (apenas palavras, sem pontuação)
        tokens = [token.text.lower() for token in doc 
                  if not token.is_punct and not token.is_space]
        
        # Calcula TTR (Type-Token Ratio)
        ttr = calculate_type_token_ratio(tokens) if tokens else 0.0
        
        # Calcula MTLD
        mtld = calculate_mtld(tokens) if len(tokens) >= 10 else 0.0
        
        # Identifica palavras repetidas
        repeated_words = count_repeated_words(tokens, min_count=4)
        
        # Deteta nominalizações
        nominalizations = detect_nominalizations(text)
        
        # Deteta marcadores típicos de IA
        ai_markers_found = detect_ai_markers(text, self.ai_markers)
        
        # Proporção de palavras únicas
        unique_words_ratio = len(set(tokens)) / len(tokens) if tokens else 0.0
        
        return {
            'ttr': round(ttr, 3),
            'mtld': round(mtld, 2),
            'repeated_words': repeated_words,
            'nominalizations': nominalizations,
            'ai_markers': ai_markers_found,
            'unique_words_ratio': round(unique_words_ratio, 3)
        }
    
    def _analyze_syntactic(self, doc, text: str) -> Dict:
        """
        Análise de métricas sintáticas (estrutura das frases).
        VERSÃO OPTIMIZADA: Adiciona métricas de pontuação sofisticada.
        
        Args:
            doc: spaCy Doc object
            text: Texto original (para análise de pontuação)
        
        Returns:
            Dicionário com métricas sintáticas expandidas
        """
        # Analisa comprimento das frases
        sentence_lengths = []
        for sent in doc.sents:
            word_count = sum(1 for token in sent if not token.is_punct and not token.is_space)
            if word_count > 0:
                sentence_lengths.append(word_count)
        
        # Média e desvio-padrão do comprimento das frases
        avg_length = statistics.mean(sentence_lengths) if sentence_lengths else 0.0
        std_dev = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0.0
        
        # Coeficiente de variação (CV) - MÉTRICA CRÍTICA
        cv = (std_dev / avg_length) if avg_length > 0 else 0.0
        
        # Conta construções de voz passiva
        passive_count = detect_passive_voice(doc)
        
        # Calcula profundidade sintática média
        syntactic_depth = self._calculate_syntactic_depth(doc)
        
        # Calcula proporção de ordem SVO
        svo_ratio = self._calculate_svo_ratio(doc)
        
        # NOVO: Análise de pontuação sofisticada
        punctuation_metrics = self._analyze_punctuation(text, len(sentence_lengths))
        
        # NOVO: Variedade de inícios de frase
        sentence_start_variety = self._analyze_sentence_starts(doc)
        
        return {
            'avg_sentence_length': round(avg_length, 1),
            'std_dev_sentence_length': round(std_dev, 2),
            'coefficient_variation': round(cv, 3),  # NOVO: CV
            'passive_voice_count': passive_count,
            'syntactic_depth': round(syntactic_depth, 2),
            'svo_ratio': round(svo_ratio, 3),
            'punctuation': punctuation_metrics,  # NOVO
            'sentence_start_variety': round(sentence_start_variety, 3)  # NOVO
        }
    
    def _analyze_punctuation(self, text: str, num_sentences: int) -> Dict:
        """
        NOVA MÉTRICA: Analisa uso de pontuação sofisticada.
        IA tende a usar apenas pontos e vírgulas básicas.
        
        Args:
            text: Texto original
            num_sentences: Número de frases
        
        Returns:
            Dict com contagens de pontuação
        """
        num_words = len(text.split())
        
        return {
            'semicolons': text.count(';'),
            'em_dashes': text.count('—') + text.count(' - ') + text.count(' – '),
            'colons': text.count(':'),
            'parentheses': text.count('('),
            'ellipsis': len(re.findall(r'\.{3,}', text)),
            # Densidades (por 1000 palavras)
            'semicolon_density': (text.count(';') / num_words * 1000) if num_words > 0 else 0,
            'dash_density': ((text.count('—') + text.count(' - ')) / num_words * 1000) if num_words > 0 else 0
        }
    
    def _analyze_sentence_starts(self, doc) -> float:
        """
        NOVA MÉTRICA: Analisa variedade de inícios de frase.
        IA tende a começar frases sempre da mesma forma.
        
        Args:
            doc: spaCy Doc object
        
        Returns:
            Score de variedade (0-1, maior = mais variado)
        """
        sentence_starts = []
        
        for sent in doc.sents:
            tokens = [t for t in sent if not t.is_punct and not t.is_space]
            if tokens:
                # Categoriza o início
                first_token = tokens[0]
                if first_token.pos_ in ['DET', 'PRON']:
                    category = 'determiner_pronoun'
                elif first_token.pos_ == 'VERB':
                    category = 'verb'
                elif first_token.pos_ in ['SCONJ', 'ADP']:
                    category = 'subordinate'
                elif first_token.pos_ == 'ADV':
                    category = 'adverb'
                else:
                    category = 'other'
                
                sentence_starts.append(category)
        
        if not sentence_starts:
            return 0.5
        
        # Calcula entropia (variedade)
        counter = Counter(sentence_starts)
        total = len(sentence_starts)
        entropy = 0
        
        for count in counter.values():
            p = count / total
            if p > 0:
                entropy -= p * (p ** 0.5)  # Penaliza repetição
        
        # Normaliza (quanto maior, mais variado)
        max_entropy = 1.0
        return min(entropy / max_entropy, 1.0)
    
    def _calculate_syntactic_depth(self, doc) -> float:
        """
        Calcula profundidade média da árvore sintática.
        
        Maior profundidade indica frases mais complexas e subordinadas.
        IA tende a ter profundidade 2-3, humanos 4-6.
        
        Args:
            doc: spaCy Doc object
        
        Returns:
            Profundidade média
        """
        def get_token_depth(token) -> int:
            """Calcula profundidade de um token na árvore"""
            depth = 0
            current = token
            while current.head != current:
                depth += 1
                current = current.head
            return depth
        
        depths = []
        for sent in doc.sents:
            sent_depths = [get_token_depth(token) for token in sent]
            if sent_depths:
                depths.append(max(sent_depths))  # Profundidade máxima da frase
        
        return statistics.mean(depths) if depths else 0.0
    
    def _calculate_svo_ratio(self, doc) -> float:
        """
        Calcula proporção de frases com ordem canónica SVO.
        
        Args:
            doc: spaCy Doc object
        
        Returns:
            Proporção de frases SVO (0-1)
        """
        svo_count = 0
        total_sentences = 0
        
        for sent in doc.sents:
            total_sentences += 1
            
            subj_pos = None
            verb_pos = None
            obj_pos = None
            
            for token in sent:
                if token.dep_ == 'nsubj':
                    subj_pos = token.i
                    verb_pos = token.head.i
                elif token.dep_ in ['obj', 'dobj']:
                    obj_pos = token.i
            
            if subj_pos is not None and verb_pos is not None and obj_pos is not None:
                if subj_pos < verb_pos < obj_pos:
                    svo_count += 1
            elif subj_pos is not None and verb_pos is not None:
                if subj_pos < verb_pos:
                    svo_count += 0.5
        
        return svo_count / total_sentences if total_sentences > 0 else 0.0
    
    def _analyze_style(self, text: str, doc) -> Dict:
        """
        Análise de métricas de estilo (tom, formalidade, personalização).
        VERSÃO OPTIMIZADA: Adiciona detecção de imperfeições naturais.
        
        Args:
            text: Texto original
            doc: spaCy Doc object
        
        Returns:
            Dicionário com métricas de estilo expandidas
        """
        # Score de impessoalidade
        impersonality = self._calculate_impersonality(text, doc)
        
        # Score de formalidade
        formality = self._calculate_formality(doc)
        
        # Conta termos de hedging
        hedging_count = detect_hedging_terms(text, self.hedging_terms)
        
        # Conta pronomes de primeira pessoa
        first_person_count = detect_first_person_pronouns(text)
        
        # Conta exclamações e reticências
        exclamation_count = text.count('!')
        ellipsis_count = len(re.findall(r'\.{3,}', text))
        
        # NOVO: Deteta imperfeições naturais
        natural_imperfections = self._detect_natural_imperfections(text)
        
        return {
            'impersonality_score': round(impersonality, 3),
            'formality_score': round(formality, 3),
            'hedging_count': hedging_count,
            'first_person_count': first_person_count,
            'exclamation_count': exclamation_count,
            'ellipsis_count': ellipsis_count,
            'natural_imperfections': natural_imperfections  # NOVO
        }
    
    def _detect_natural_imperfections(self, text: str) -> Dict:
        """
        NOVA MÉTRICA: Deteta "imperfeições" que humanos fazem mas IA evita.
        
        Args:
            text: Texto original
        
        Returns:
            Dict com contagens de imperfeições naturais
        """
        return {
            'starts_with_and_but': len(re.findall(r'\.\s+(E|Mas)\s+[a-z]', text)),
            'sentence_fragments': len(re.findall(r'\?\s+[A-Z][a-zá-ú]+\.', text)),
            'self_corrections': len(re.findall(r'ou melhor|ou seja|isto é|quer dizer|bem,', text.lower())),
            'rhetorical_questions': text.count('?') - (1 if text.rstrip().endswith('?') else 0),
            'parenthetical_asides': len(re.findall(r'\([^)]{5,50}\)', text)),  # Apartes entre parênteses
            'hesitations': len(re.findall(r'\.{3,}|, bem,|, digamos,', text.lower()))
        }
    
    def _calculate_impersonality(self, text: str, doc) -> float:
        """
        Calcula score de impessoalidade (0-1, maior = mais impessoal).
        
        Args:
            text: Texto original
            doc: spaCy Doc object
        
        Returns:
            Score 0-1 (0=pessoal, 1=muito impessoal)
        """
        personal_pronouns = detect_first_person_pronouns(text)
        
        second_person = len(re.findall(
            r'\b(tu|te|ti|contigo|teu|tua|teus|tuas|você|vocês)\b',
            text.lower()
        ))
        
        total_personal = personal_pronouns + second_person
        
        word_count = len([t for t in doc if not t.is_punct and not t.is_space])
        
        personal_ratio = total_personal / word_count if word_count > 0 else 0
        
        passive_count = detect_passive_voice(doc)
        sentence_count = len(list(doc.sents))
        passive_ratio = passive_count / sentence_count if sentence_count > 0 else 0
        
        impersonal_constructions = len(re.findall(
            r'\b(verifica-se|observa-se|constata-se|nota-se|deve-se|pode-se|há que|é necessário)\b',
            text.lower()
        ))
        impersonal_ratio = impersonal_constructions / sentence_count if sentence_count > 0 else 0
        
        impersonality = (
            (1 - personal_ratio) * 0.4 +
            passive_ratio * 0.3 +
            min(impersonal_ratio, 1.0) * 0.3
        )
        
        return min(impersonality, 1.0)
    
    def _calculate_formality(self, doc) -> float:
        """
        Calcula score de formalidade usando F-score de Heylighen adaptado.
        
        Args:
            doc: spaCy Doc object
        
        Returns:
            Score 0-1 (0=informal, 1=muito formal)
        """
        pos_counts = Counter([token.pos_ for token in doc if not token.is_punct])
        
        noun = pos_counts.get('NOUN', 0) + pos_counts.get('PROPN', 0)
        adj = pos_counts.get('ADJ', 0)
        prep = pos_counts.get('ADP', 0)
        article = pos_counts.get('DET', 0)
        pronoun = pos_counts.get('PRON', 0)
        verb = pos_counts.get('VERB', 0) + pos_counts.get('AUX', 0)
        adverb = pos_counts.get('ADV', 0)
        interjection = pos_counts.get('INTJ', 0)
        
        total = sum(pos_counts.values())
        
        if total == 0:
            return 0.5
        
        noun_norm = (noun / total) * 100
        adj_norm = (adj / total) * 100
        prep_norm = (prep / total) * 100
        article_norm = (article / total) * 100
        pronoun_norm = (pronoun / total) * 100
        verb_norm = (verb / total) * 100
        adverb_norm = (adverb / total) * 100
        interjection_norm = (interjection / total) * 100
        
        f_score = (
            noun_norm + adj_norm + prep_norm + article_norm 
            - pronoun_norm - verb_norm - adverb_norm - interjection_norm 
            + 100
        ) / 200
        
        return max(0.0, min(1.0, f_score))
    
    def _analyze_structure(self, text: str) -> Dict:
        """
        Análise de métricas estruturais (organização do texto).
        
        Args:
            text: Texto a analisar
        
        Returns:
            Dicionário com métricas estruturais
        """
        has_formulaic_intro = detect_formulaic_intro(text)
        has_formulaic_conclusion = detect_formulaic_conclusion(text)
        
        transition_markers = count_transition_markers(text)
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        
        if paragraph_count > 0:
            total_sentences = text.count('.') + text.count('!') + text.count('?')
            avg_paragraph_length = total_sentences / paragraph_count
        else:
            avg_paragraph_length = 0.0
        
        return {
            'has_formulaic_intro': has_formulaic_intro,
            'has_formulaic_conclusion': has_formulaic_conclusion,
            'transition_markers': transition_markers,
            'paragraph_count': paragraph_count,
            'avg_paragraph_length': round(avg_paragraph_length, 1)
        }
    
    def _calculate_ai_score(self, metrics: Dict, text: str) -> Dict:
        """
        VERSÃO ULTRA-RIGOROSA: Combina todas as métricas num score global 0-100.
        
        MUDANÇAS:
        - Thresholds MUITO mais apertados
        - Pesos rebalanceados (mais peso nas métricas críticas)
        - Novas métricas incluídas (pontuação, imperfeições)
        - Sistema de penalizações mais severo
        
        Quanto MAIOR o score, mais parece texto humano.
        Quanto MENOR o score, mais parece IA.
        
        Args:
            metrics: Dicionário com todas as métricas
            text: Texto original (para cálculos adicionais)
        
        Returns:
            Dict com score final e breakdown detalhado
        """
        lex = metrics['lexical']
        syn = metrics['syntactic']
        sty = metrics['style']
        struct = metrics['structure']
        
        scores = {}
        
        # =================================================================
        # 1. VARIAÇÃO DE COMPRIMENTO - PESO 20% (antes 15%)
        # =================================================================
        cv = syn['coefficient_variation']
        
        # THRESHOLDS MUITO MAIS APERTADOS
        if cv < 0.10:
            variation_score = 0
        elif cv < 0.20:
            variation_score = 20
        elif cv < 0.30:
            variation_score = 40
        elif cv < 0.40:
            variation_score = 65
        elif cv < 0.50:
            variation_score = 80
        else:
            variation_score = 95
        
        scores['sentence_variation'] = variation_score * 0.20
        
        # =================================================================
        # 2. PONTUAÇÃO SOFISTICADA - PESO 15% (NOVA!)
        # =================================================================
        punct = syn['punctuation']
        punct_score = 0
        
        # Ponto e vírgula: exige pelo menos 3 num texto médio
        if punct['semicolons'] >= 5:
            punct_score += 40
        elif punct['semicolons'] >= 3:
            punct_score += 25
        elif punct['semicolons'] >= 1:
            punct_score += 10
        
        # Travessões: exige pelo menos 2
        if punct['em_dashes'] >= 4:
            punct_score += 35
        elif punct['em_dashes'] >= 2:
            punct_score += 20
        elif punct['em_dashes'] >= 1:
            punct_score += 5
        
        # Parênteses: exige pelo menos 3
        if punct['parentheses'] >= 6:
            punct_score += 25
        elif punct['parentheses'] >= 3:
            punct_score += 15
        elif punct['parentheses'] >= 1:
            punct_score += 5
        
        scores['punctuation_sophistication'] = min(punct_score, 100) * 0.15
        
        # =================================================================
        # 3. COMPLEXIDADE SINTÁTICA - PESO 15% (antes implícito)
        # =================================================================
        depth = syn['syntactic_depth']
        
        # MUITO MAIS APERTADO (IA tem depth ~2-3, humano ~4-6)
        if depth < 2.0:
            depth_score = 10
        elif depth < 3.0:
            depth_score = 30
        elif depth < 4.0:
            depth_score = 55
        elif depth < 5.5:
            depth_score = 80
        else:
            depth_score = 95
        
        scores['syntactic_complexity'] = depth_score * 0.15
        
        # =================================================================
        # 4. MARCADORES IA - PESO 18% (antes 20%, ligeiramente reduzido)
        # =================================================================
        ai_markers_count = len(lex['ai_markers'])
        
        # MAIS RIGOROSO: cada marcador penaliza 15 pontos (antes 10)
        ai_markers_penalty = min(ai_markers_count * 15, 100)
        ai_markers_score = max(100 - ai_markers_penalty, 0)
        scores['ai_markers'] = ai_markers_score * 0.18
        
        # =================================================================
        # 5. IMPESSOALIDADE - PESO 12% (antes 20%, reduzido)
        # =================================================================
        # Inverte: quanto menor impessoalidade, maior score
        impersonality_score = (1 - sty['impersonality_score']) * 100
        scores['personality'] = impersonality_score * 0.12
        
        # =================================================================
        # 6. DIVERSIDADE LEXICAL (TTR) - PESO 10% (antes 15%)
        # =================================================================
        # Threshold mais apertado: TTR ideal > 0.50 (antes 0.45)
        ttr_score = min(lex['ttr'] / 0.50, 1.0) * 100
        scores['lexical_diversity'] = ttr_score * 0.10
        
        # =================================================================
        # 7. FORMALIDADE - PESO 8% (antes 10%)
        # =================================================================
        # Threshold mais apertado: formalidade ideal < 0.65 (antes 0.70)
        formality_score = (1 - min(sty['formality_score'] / 0.65, 1.0)) * 100
        scores['formality'] = formality_score * 0.08
        
        # =================================================================
        # 8. IMPERFEIÇÕES NATURAIS - PESO 12% (NOVA!)
        # =================================================================
        imperfs = sty['natural_imperfections']
        imperf_score = 0
        
        # Bónus por cada tipo de imperfeição
        if imperfs['starts_with_and_but'] > 0:
            imperf_score += 30
        if imperfs['sentence_fragments'] > 0:
            imperf_score += 25
        if imperfs['self_corrections'] > 0:
            imperf_score += 20
        if imperfs['rhetorical_questions'] > 0:
            imperf_score += 15
        if imperfs['parenthetical_asides'] > 0:
            imperf_score += 10
        
        scores['natural_imperfections'] = min(imperf_score, 100) * 0.12
        
        # =================================================================
        # PENALIZAÇÕES SEVERAS
        # =================================================================
        penalties = 0
        
        # Introdução/conclusão formulaica - PENALIZAÇÃO BRUTAL
        if struct['has_formulaic_intro']:
            penalties += 15  # Antes 5
        if struct['has_formulaic_conclusion']:
            penalties += 15  # Antes 5
        
        # Voz passiva excessiva - MAIS RIGOROSO
        if syn['passive_voice_count'] > 3:  # Antes 5
            penalties += (syn['passive_voice_count'] - 3) * 3  # Antes *2
        
        # Marcadores de transição - MAIS RIGOROSO
        if struct['transition_markers'] > 2:  # Antes 3
            penalties += (struct['transition_markers'] - 2) * 3  # Antes *2
        
        # NOVA PENALIZAÇÃO: Sem ponto e vírgula em texto longo
        word_count = len(text.split())
        if word_count > 200 and punct['semicolons'] == 0:
            penalties += 12
        
        # NOVA PENALIZAÇÃO: Sem travessões em texto longo
        if word_count > 200 and punct['em_dashes'] == 0:
            penalties += 10
        
        # NOVA PENALIZAÇÃO: Zero pronomes pessoais
        if sty['first_person_count'] == 0 and word_count > 150:
            penalties += 10
        
        # NOVA PENALIZAÇÃO: Variação de início de frase baixa
        if syn['sentence_start_variety'] < 0.3:
            penalties += 8
        
        # NOVA PENALIZAÇÃO: Nominalizações excessivas - MAIS RIGOROSO
        nom_count = len(lex['nominalizations'])
        if nom_count > 2:  # Antes 3
            penalties += (nom_count - 2) * 5  # Antes *10, mas agora threshold menor
        
        # =================================================================
        # BÓNUS (menos generosos)
        # =================================================================
        bonus = 0
        
        # Bónus por pronomes pessoais - REDUZIDO
        if sty['first_person_count'] > 0:
            bonus += min(sty['first_person_count'] * 1.5, 5)  # Antes *2, max 8
        
        # Bónus por exclamações - REDUZIDO
        if sty['exclamation_count'] > 0:
            bonus += min(sty['exclamation_count'] * 0.5, 2)  # Antes *1, max 3
        
        # Bónus por reticências - REDUZIDO
        if sty['ellipsis_count'] > 0:
            bonus += min(sty['ellipsis_count'] * 1, 3)  # Antes *2, max 4
        
        # =================================================================
        # SCORE FINAL
        # =================================================================
        base_score = sum(scores.values())
        final_score = base_score + bonus - penalties
        
        # Garante que está entre 0 e 100
        final_score = max(0, min(100, final_score))
        
        return {
            'final_score': int(round(final_score)),
            'base_score': round(base_score, 1),
            'bonus': round(bonus, 1),
            'penalties': round(penalties, 1),
            'component_scores': {k: round(v, 1) for k, v in scores.items()},
            'verdict': self._get_verdict(final_score)
        }
    
    def _get_verdict(self, score: float) -> str:
        """
        Retorna veredicto baseado no score.
        
        Args:
            score: Score 0-100
        
        Returns:
            String com veredicto
        """
        if score < 25:  # Antes 30
            return "🚨 Muito claramente IA"
        elif score < 45:  # Antes 50
            return "⚠️  Provavelmente IA"
        elif score < 65:  # Antes 70
            return "🤔 Ambíguo (melhorado mas ainda com padrões IA)"
        elif score < 85:  # Antes 90
            return "✅ Provavelmente humano"
        else:
            return "✅ Muito provavelmente humano"