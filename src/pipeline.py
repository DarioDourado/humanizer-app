"""
Gerador de pipeline de transformações.

Este módulo decide que prompts aplicar baseado no diagnóstico do texto,
priorizando as transformações mais necessárias.
"""

from typing import List, Tuple, Dict


class PipelineGenerator:
    """
    Gerador de pipeline que decide quais transformações aplicar.
    
    Analisa o diagnóstico do texto e gera lista ordenada de prompts a aplicar,
    priorizando os problemas mais críticos.
    
    Ordem de prioridade:
    1. Problemas lexicais (diversidade, nominalizações)
    2. Problemas sintáticos (ritmo, voz passiva)
    3. Problemas de estilo (impessoalidade, formalidade)
    4. Problemas de estrutura (marcadores IA, estrutura formulaica)
    
    Attributes:
        THRESHOLDS: Dicionário com thresholds de decisão
    """
    
    # Thresholds para decisão (podem ser ajustados empiricamente)
    THRESHOLDS = {
        'ttr_min': 0.45,                # Type-Token Ratio mínimo aceitável
        'nominalizations_max': 3,       # Máximo de nominalizações aceitável
        'burstiness_min': 3.0,          # Desvio-padrão mínimo de comprimento de frases
        'passive_voice_max': 5,         # Máximo de construções passivas aceitável
        'impersonality_max': 0.7,       # Score máximo de impessoalidade
        'formality_max': 0.75,          # Score máximo de formalidade
        'ai_markers_max': 2,            # Máximo de marcadores IA aceitável
        'hedging_max': 5,               # Máximo de termos hedging aceitável
        'first_person_min': 1           # Mínimo de pronomes 1ª pessoa desejável
    }
    
    def __init__(self, thresholds: Dict = None):
        """
        Inicializa gerador com thresholds personalizados (opcional).
        
        Args:
            thresholds: Dicionário com thresholds customizados (sobrescreve defaults)
        """
        if thresholds:
            self.THRESHOLDS = {**self.THRESHOLDS, **thresholds}
    
    def generate(self, diagnosis: Dict) -> List[Tuple[str, Dict]]:
        """
        Gera lista ordenada de transformações a aplicar.
        
        Args:
            diagnosis: Output do TextAnalyzer.analyze() com todas as métricas
        
        Returns:
            Lista de tuplos (prompt_id, params_dict) ordenada por prioridade.
            
            Exemplo:
            [
                ('LEXICO_DIVERSIFICAR', {'ttr_atual': 0.32, 'palavras_repetidas': {...}}),
                ('SINTAXE_VARIAR_RITMO', {'std_dev': 1.8, 'avg_length': 15.2}),
                ...
            ]
        
        Examples:
            >>> generator = PipelineGenerator()
            >>> diagnosis = analyzer.analyze("Texto...")
            >>> pipeline = generator.generate(diagnosis)
            >>> for prompt_id, params in pipeline:
            ...     print(f"Aplicar: {prompt_id}")
        """
        pipeline = []
        
        # Extrai métricas por categoria
        lex = diagnosis['lexical']
        syn = diagnosis['syntactic']
        sty = diagnosis['style']
        struct = diagnosis['structure']
        
        # ========== PRIORIDADE 1: PROBLEMAS LEXICAIS ==========
        
        # 1.1 Diversidade lexical baixa
        if lex['ttr'] < self.THRESHOLDS['ttr_min']:
            pipeline.append((
                'LEXICO_DIVERSIFICAR',
                {
                    'ttr_atual': lex['ttr'],
                    'palavras_repetidas': str(lex['repeated_words'])
                }
            ))
        
        # 1.2 Nominalizações excessivas
        if len(lex['nominalizations']) > self.THRESHOLDS['nominalizations_max']:
            pipeline.append((
                'LEXICO_DESNOMINALIZAR',
                {
                    'nominalizacoes': ', '.join(lex['nominalizations'][:10])  # Limita a 10 para não saturar prompt
                }
            ))
        
        # ========== PRIORIDADE 2: PROBLEMAS SINTÁTICOS ==========
        
        # 2.1 Falta de variação no ritmo (burstiness baixo)
        if syn['std_dev_sentence_length'] < self.THRESHOLDS['burstiness_min']:
            pipeline.append((
                'SINTAXE_VARIAR_RITMO',
                {
                    'std_dev': syn['std_dev_sentence_length'],
                    'avg_length': syn['avg_sentence_length']
                }
            ))
        
        # 2.2 Voz passiva excessiva
        if syn['passive_voice_count'] > self.THRESHOLDS['passive_voice_max']:
            pipeline.append((
                'SINTAXE_ATIVAR_VOZ',
                {
                    'passivas_count': syn['passive_voice_count']
                }
            ))
        
        # ========== PRIORIDADE 3: PROBLEMAS DE ESTILO ==========
        
        # 3.1 Impessoalidade excessiva
        if sty['impersonality_score'] > self.THRESHOLDS['impersonality_max']:
            pipeline.append((
                'ESTILO_PESSOALIZAR',
                {
                    'impersonality_score': sty['impersonality_score'],
                    'first_person_count': sty['first_person_count']
                }
            ))
        
        # 3.2 Formalidade excessiva
        if sty['formality_score'] > self.THRESHOLDS['formality_max']:
            pipeline.append((
                'ESTILO_INFORMALIZAR',
                {
                    'formality_score': sty['formality_score']
                }
            ))
        
        # ========== PRIORIDADE 4: PROBLEMAS DE ESTRUTURA ==========
        
        # 4.1 Marcadores típicos de IA
        if len(lex['ai_markers']) > self.THRESHOLDS['ai_markers_max']:
            pipeline.append((
                'ESTRUTURA_LIMPAR_MARCADORES',
                {
                    'marcadores': '\n   - '.join(lex['ai_markers'])
                }
            ))
        
        # 4.2 Estrutura formulaica (intro/conclusão)
        if struct['has_formulaic_intro'] or struct['has_formulaic_conclusion']:
            pipeline.append((
                'ESTRUTURA_REORGANIZAR',
                {}
            ))
        
        return pipeline
    
    def generate_prioritized(
        self, 
        diagnosis: Dict, 
        max_transformations: int = 3
    ) -> List[Tuple[str, Dict]]:
        """
        Gera pipeline limitado às N transformações mais importantes.
        
        Útil quando se quer focar nos problemas mais críticos sem saturar
        o processo com muitas transformações.
        
        Args:
            diagnosis: Output do TextAnalyzer.analyze()
            max_transformations: Número máximo de transformações a incluir
        
        Returns:
            Lista de tuplos (prompt_id, params_dict) com no máximo N items
        
        Examples:
            >>> pipeline = generator.generate_prioritized(diagnosis, max_transformations=2)
            >>> # Retorna apenas as 2 transformações mais críticas
        """
        full_pipeline = self.generate(diagnosis)
        
        # Limita ao número máximo
        return full_pipeline[:max_transformations]
    
    def get_problem_summary(self, diagnosis: Dict) -> Dict:
        """
        Gera resumo dos problemas encontrados no texto.
        
        Args:
            diagnosis: Output do TextAnalyzer.analyze()
        
        Returns:
            Dicionário com resumo estruturado dos problemas por categoria
        
        Examples:
            >>> summary = generator.get_problem_summary(diagnosis)
            >>> print(f"Problemas lexicais: {len(summary['lexical'])}")
        """
        problems = {
            'lexical': [],
            'syntactic': [],
            'style': [],
            'structure': []
        }
        
        lex = diagnosis['lexical']
        syn = diagnosis['syntactic']
        sty = diagnosis['style']
        struct = diagnosis['structure']
        
        # Identifica problemas lexicais
        if lex['ttr'] < self.THRESHOLDS['ttr_min']:
            problems['lexical'].append(
                f"Baixa diversidade lexical (TTR: {lex['ttr']:.2f}, ideal: >{self.THRESHOLDS['ttr_min']})"
            )
        
        if len(lex['nominalizations']) > self.THRESHOLDS['nominalizations_max']:
            problems['lexical'].append(
                f"Nominalizações excessivas ({len(lex['nominalizations'])} encontradas, ideal: ≤{self.THRESHOLDS['nominalizations_max']})"
            )
        
        if len(lex['ai_markers']) > self.THRESHOLDS['ai_markers_max']:
            problems['lexical'].append(
                f"Marcadores IA ({len(lex['ai_markers'])} encontrados, ideal: ≤{self.THRESHOLDS['ai_markers_max']})"
            )
        
        # Identifica problemas sintáticos
        if syn['std_dev_sentence_length'] < self.THRESHOLDS['burstiness_min']:
            problems['syntactic'].append(
                f"Frases muito uniformes (desvio: {syn['std_dev_sentence_length']:.1f}, ideal: >{self.THRESHOLDS['burstiness_min']})"
            )
        
        if syn['passive_voice_count'] > self.THRESHOLDS['passive_voice_max']:
            problems['syntactic'].append(
                f"Voz passiva excessiva ({syn['passive_voice_count']} construções, ideal: ≤{self.THRESHOLDS['passive_voice_max']})"
            )
        
        # Identifica problemas de estilo
        if sty['impersonality_score'] > self.THRESHOLDS['impersonality_max']:
            problems['style'].append(
                f"Muito impessoal (score: {sty['impersonality_score']:.2f}, ideal: ≤{self.THRESHOLDS['impersonality_max']})"
            )
        
        if sty['formality_score'] > self.THRESHOLDS['formality_max']:
            problems['style'].append(
                f"Muito formal (score: {sty['formality_score']:.2f}, ideal: ≤{self.THRESHOLDS['formality_max']})"
            )
        
        if sty['first_person_count'] < self.THRESHOLDS['first_person_min']:
            problems['style'].append(
                f"Falta voz pessoal ({sty['first_person_count']} pronomes 1ª pessoa, ideal: ≥{self.THRESHOLDS['first_person_min']})"
            )
        
        # Identifica problemas de estrutura
        if struct['has_formulaic_intro']:
            problems['structure'].append("Introdução formulaica detectada")
        
        if struct['has_formulaic_conclusion']:
            problems['structure'].append("Conclusão formulaica detectada")
        
        if struct['transition_markers'] > 3:
            problems['structure'].append(
                f"Marcadores de transição excessivos ({struct['transition_markers']})"
            )
        
        return problems
    
    def should_continue(self, diagnosis: Dict, target_score: int = 70) -> bool:
        """
        Verifica se há problemas suficientes para justificar mais transformações.
        
        Args:
            diagnosis: Output do TextAnalyzer.analyze()
            target_score: Score objetivo
        
        Returns:
            True se deve continuar transformando, False se já está bom
        
        Examples:
            >>> if generator.should_continue(diagnosis):
            ...     pipeline = generator.generate(diagnosis)
            ... else:
            ...     print("Texto já está satisfatório")
        """
        # Se já atingiu target, não precisa continuar
        if diagnosis['score'] >= target_score:
            return False
        
        # Se ainda há transformações a fazer, continua
        pipeline = self.generate(diagnosis)
        return len(pipeline) > 0
