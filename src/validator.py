"""
Validador de transformações de texto.

Este módulo compara texto antes e depois de transformações para verificar
se houve melhoria efetiva no score de humanização.
"""

from typing import Dict


class Validator:
    """
    Valida se transformação de texto resultou em melhoria.
    
    Compara scores antes e depois, fornece recomendação sobre próximos passos
    e detecta transformações que pioraram o texto.
    
    Attributes:
        analyzer: Instância de TextAnalyzer para análise de texto
    """
    
    def __init__(self, analyzer):
        """
        Inicializa validador com analisador de texto.
        
        Args:
            analyzer: Instância de TextAnalyzer configurada
        """
        self.analyzer = analyzer
    
    def validate(self, original_text: str, transformed_text: str) -> Dict:
        """
        Compara scores antes e depois da transformação.
        
        Args:
            original_text: Texto antes da transformação
            transformed_text: Texto depois da transformação
        
        Returns:
            Dicionário com:
            {
                'improved': bool,              # Se houve melhoria
                'score_before': int,           # Score original (0-100)
                'score_after': int,            # Score após transformação (0-100)
                'improvement': int,            # Diferença (pode ser negativa)
                'recommendation': str,         # Próximo passo recomendado
                'analysis_before': dict,       # Análise completa do texto original
                'analysis_after': dict         # Análise completa do texto transformado
            }
            
            recommendation pode ser:
            - 'success': Atingiu score satisfatório (≥60), pode parar
            - 'continue_pipeline': Melhorou mas ainda precisa mais transformações
            - 'transformation_failed': Não melhorou significativamente, tentar outra abordagem
        
        Examples:
            >>> validator = Validator(analyzer)
            >>> result = validator.validate("Texto original...", "Texto modificado...")
            >>> if result['improved']:
            ...     print(f"Melhorou +{result['improvement']} pontos")
        """
        # Analisa ambos os textos
        analysis_before = self.analyzer.analyze(original_text)
        analysis_after = self.analyzer.analyze(transformed_text)
        
        score_before = analysis_before['score']
        score_after = analysis_after['score']
        improvement = score_after - score_before
        
        # Determina se melhorou
        improved = improvement >= 3  # Melhoria mínima de 3 pontos
        
        # Determina recomendação
        recommendation = self._get_recommendation(
            score_after, 
            improvement, 
            improved
        )
        
        return {
            'improved': improved,
            'score_before': score_before,
            'score_after': score_after,
            'improvement': improvement,
            'recommendation': recommendation,
            'analysis_before': analysis_before,
            'analysis_after': analysis_after
        }
    
    def _get_recommendation(
        self, 
        score_after: int, 
        improvement: int, 
        improved: bool
    ) -> str:
        """
        Determina próximo passo recomendado baseado em score e melhoria.
        
        Args:
            score_after: Score após transformação
            improvement: Diferença de score
            improved: Se houve melhoria significativa
        
        Returns:
            String com recomendação: 'success', 'continue_pipeline', 'transformation_failed'
        """
        # Caso 1: Score satisfatório atingido
        if score_after >= 60:
            return 'success'
        
        # Caso 2: Melhorou significativamente mas ainda abaixo do target
        if improved and score_after < 60:
            return 'continue_pipeline'
        
        # Caso 3: Não melhorou significativamente
        if not improved:
            # Se piorou muito, definitivamente falhou
            if improvement < -5:
                return 'transformation_failed'
            # Se melhorou muito pouco (< 3 pontos), também falhou
            return 'transformation_failed'
        
        # Fallback
        return 'continue_pipeline'
    
    def validate_batch(
        self, 
        original_text: str, 
        transformed_texts: list
    ) -> Dict:
        """
        Valida múltiplas transformações e escolhe a melhor.
        
        Útil quando se aplica diferentes prompts e quer escolher
        o melhor resultado.
        
        Args:
            original_text: Texto original
            transformed_texts: Lista de textos transformados para comparar
        
        Returns:
            Dicionário com:
            {
                'best_index': int,           # Índice do melhor texto
                'best_text': str,            # Melhor texto transformado
                'best_score': int,           # Score do melhor
                'all_results': list[dict]    # Validações de todos os textos
            }
        
        Examples:
            >>> results = validator.validate_batch(
            ...     "Original...",
            ...     ["Transformação 1...", "Transformação 2..."]
            ... )
            >>> best = results['best_text']
        """
        all_results = []
        
        for i, transformed_text in enumerate(transformed_texts):
            result = self.validate(original_text, transformed_text)
            result['index'] = i
            all_results.append(result)
        
        # Encontra melhor score
        best_result = max(all_results, key=lambda x: x['score_after'])
        
        return {
            'best_index': best_result['index'],
            'best_text': transformed_texts[best_result['index']],
            'best_score': best_result['score_after'],
            'all_results': all_results
        }
    
    def get_improvement_summary(self, validation_result: Dict) -> str:
        """
        Gera resumo textual da validação para output legível.
        
        Args:
            validation_result: Output do método validate()
        
        Returns:
            String formatada com resumo da validação
        
        Examples:
            >>> result = validator.validate(original, transformed)
            >>> print(validator.get_improvement_summary(result))
            '✓ Melhorou +8 pontos (45 → 53). Continuar pipeline.'
        """
        score_before = validation_result['score_before']
        score_after = validation_result['score_after']
        improvement = validation_result['improvement']
        recommendation = validation_result['recommendation']
        improved = validation_result['improved']
        
        # Símbolo baseado em melhoria
        symbol = "✓" if improved else "✗"
        
        # Direção da mudança
        if improvement > 0:
            direction = f"+{improvement}"
        elif improvement < 0:
            direction = f"{improvement}"
        else:
            direction = "±0"
        
        # Recomendação em português
        rec_map = {
            'success': 'Objetivo atingido!',
            'continue_pipeline': 'Continuar pipeline',
            'transformation_failed': 'Transformação falhou'
        }
        rec_text = rec_map.get(recommendation, recommendation)
        
        return (
            f"{symbol} {direction} pontos "
            f"({score_before} → {score_after}). "
            f"{rec_text}."
        )
    
    def compare_metrics(
        self, 
        analysis_before: Dict, 
        analysis_after: Dict
    ) -> Dict:
        """
        Compara métricas específicas antes e depois.
        
        Útil para debug e entender quais aspectos melhoraram.
        
        Args:
            analysis_before: Análise do texto original
            analysis_after: Análise do texto transformado
        
        Returns:
            Dicionário com comparação de métricas principais
        
        Examples:
            >>> comparison = validator.compare_metrics(
            ...     result['analysis_before'],
            ...     result['analysis_after']
            ... )
            >>> print(f"TTR: {comparison['lexical']['ttr']['change']}")
        """
        def calculate_change(before, after):
            """Calcula mudança e direção"""
            change = after - before
            direction = 'improved' if change > 0 else ('worsened' if change < 0 else 'unchanged')
            return {
                'before': before,
                'after': after,
                'change': change,
                'direction': direction
            }
        
        return {
            'lexical': {
                'ttr': calculate_change(
                    analysis_before['lexical']['ttr'],
                    analysis_after['lexical']['ttr']
                ),
                'nominalizations_count': calculate_change(
                    len(analysis_before['lexical']['nominalizations']),
                    len(analysis_after['lexical']['nominalizations'])
                ),
                'ai_markers_count': calculate_change(
                    len(analysis_before['lexical']['ai_markers']),
                    len(analysis_after['lexical']['ai_markers'])
                )
            },
            'syntactic': {
                'burstiness': calculate_change(
                    analysis_before['syntactic']['std_dev_sentence_length'],
                    analysis_after['syntactic']['std_dev_sentence_length']
                ),
                'passive_voice': calculate_change(
                    analysis_before['syntactic']['passive_voice_count'],
                    analysis_after['syntactic']['passive_voice_count']
                )
            },
            'style': {
                'impersonality': calculate_change(
                    analysis_before['style']['impersonality_score'],
                    analysis_after['style']['impersonality_score']
                ),
                'formality': calculate_change(
                    analysis_before['style']['formality_score'],
                    analysis_after['style']['formality_score']
                ),
                'first_person': calculate_change(
                    analysis_before['style']['first_person_count'],
                    analysis_after['style']['first_person_count']
                )
            }
        }
