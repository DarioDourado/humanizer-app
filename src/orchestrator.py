"""
Orquestrador principal do sistema de humanização de texto.

Este módulo coordena todo o processo iterativo de análise, transformação e validação,
integrando todos os componentes do sistema.
"""

from typing import Dict, Optional
from .analyzer import TextAnalyzer
from .prompts import PromptLibrary
from .executor import PromptExecutor
from .validator import Validator
from .pipeline import PipelineGenerator


class HumanizationOrchestrator:
    """
    Motor principal que coordena todo o processo de humanização.
    
    Implementa loop iterativo:
    1. Analisa texto atual
    2. Verifica se atingiu target
    3. Gera pipeline de transformações necessárias
    4. Aplica cada transformação via Claude API
    5. Valida melhorias
    6. Repete até atingir target ou max_iterations
    
    Attributes:
        analyzer: Instância de TextAnalyzer
        pipeline_gen: Instância de PipelineGenerator
        executor: Instância de PromptExecutor
        validator: Instância de Validator
        prompt_lib: Instância de PromptLibrary
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        spacy_model: str = "pt_core_news_lg"
    ):
        """
        Inicializa todos os componentes do sistema.
        
        Args:
            api_key: Chave de API da Anthropic (se None, lê de variável ambiente)
            spacy_model: Modelo spaCy a usar (padrão: pt_core_news_lg)
        
        Raises:
            ValueError: Se API key não for fornecida
            OSError: Se modelo spaCy não estiver instalado
        """
        # Inicializa componentes
        self.analyzer = TextAnalyzer(model=spacy_model)
        self.pipeline_gen = PipelineGenerator()
        self.executor = PromptExecutor(api_key=api_key)
        self.validator = Validator(self.analyzer)
        self.prompt_lib = PromptLibrary()
        
        print("✓ Sistema de humanização inicializado")
    
    def humanize(
        self, 
        ai_text: str, 
        target_score: int = 70, 
        max_iterations: int = 5, 
        verbose: bool = True
    ) -> Dict:
        """
        Processo completo de humanização com loop iterativo.
        
        Este é o método principal do sistema. Recebe texto gerado por IA
        e aplica transformações iterativas até atingir score objetivo.
        
        Args:
            ai_text: Texto gerado por IA a humanizar
            target_score: Score objetivo 0-100 (padrão: 70)
            max_iterations: Número máximo de iterações (padrão: 5)
            verbose: Se True, imprime progresso detalhado
        
        Returns:
            Dicionário com:
            {
                'success': bool,              # Se atingiu target_score
                'original_text': str,         # Texto original
                'final_text': str,            # Texto final humanizado
                'original_score': int,        # Score inicial
                'final_score': int,           # Score final
                'iterations': int,            # Número de iterações executadas
                'history': list[dict],        # Histórico detalhado de cada iteração
                'message': str                # Mensagem de status (opcional)
            }
        
        Examples:
            >>> orchestrator = HumanizationOrchestrator(api_key="sk-...")
            >>> result = orchestrator.humanize(
            ...     "É importante notar que a implementação...",
            ...     target_score=70,
            ...     verbose=True
            ... )
            >>> print(result['final_text'])
        """
        current_text = ai_text
        iteration = 0
        history = []
        
        # Análise inicial
        if verbose:
            print("\n" + "="*60)
            print("🔍 ANÁLISE INICIAL")
            print("="*60)
        
        initial_diagnosis = self.analyzer.analyze(ai_text)
        original_score = initial_diagnosis['score']
        
        if verbose:
            print(f"📊 Score inicial: {original_score}/100")
            self._print_diagnosis_summary(initial_diagnosis)
        
        # Loop iterativo
        while iteration < max_iterations:
            iteration += 1
            
            if verbose:
                print("\n" + "="*60)
                print(f"🔄 ITERAÇÃO {iteration}/{max_iterations}")
                print("="*60)
            
            # 1. Diagnostica texto atual
            diagnosis = self.analyzer.analyze(current_text)
            current_score = diagnosis['score']
            
            if verbose:
                print(f"📊 Score atual: {current_score}/100")
            
            # 2. Verifica se atingiu objetivo
            if current_score >= target_score:
                if verbose:
                    print(f"\n✅ OBJETIVO ATINGIDO!")
                    print(f"Score final: {current_score}/100")
                    print(f"Melhoria total: +{current_score - original_score} pontos")
                
                return {
                    'success': True,
                    'original_text': ai_text,
                    'final_text': current_text,
                    'original_score': original_score,
                    'final_score': current_score,
                    'iterations': iteration - 1,  # Não contabiliza iteração que só verificou
                    'history': history
                }
            
            # 3. Gera pipeline de transformações
            pipeline = self.pipeline_gen.generate(diagnosis)
            
            if not pipeline:
                if verbose:
                    print("\n⚠️  Sem mais transformações disponíveis")
                    print(f"Score final: {current_score}/100 (target: {target_score})")
                break
            
            if verbose:
                print(f"\n📋 Pipeline gerado ({len(pipeline)} transformações):")
                for i, (prompt_id, _) in enumerate(pipeline, 1):
                    desc = self.prompt_lib.get_prompt_description(prompt_id)
                    print(f"   {i}. {prompt_id}: {desc}")
            
            # 4. Aplica cada transformação do pipeline
            iteration_improvements = []
            iteration_start_text = current_text
            iteration_start_score = current_score
            
            for idx, (prompt_id, params) in enumerate(pipeline, 1):
                if verbose:
                    print(f"\n   🔧 [{idx}/{len(pipeline)}] {prompt_id}...", end=' ')
                
                try:
                    # Constrói prompt
                    prompt = self.prompt_lib.build_prompt(
                        prompt_id, 
                        current_text, 
                        params
                    )
                    
                    # Executa via Claude API
                    transformed_text = self.executor.execute(prompt)
                    
                    # Valida transformação
                    validation = self.validator.validate(
                        current_text, 
                        transformed_text
                    )
                    
                    # Se melhorou, aceita transformação
                    if validation['improved']:
                        current_text = transformed_text
                        
                        if verbose:
                            print(f"✓ (+{validation['improvement']} pontos)")
                        
                        iteration_improvements.append({
                            'prompt_id': prompt_id,
                            'improvement': validation['improvement'],
                            'score_after': validation['score_after']
                        })
                    else:
                        if verbose:
                            change = validation['improvement']
                            if change < 0:
                                print(f"✗ (piorou {change} pontos)")
                            else:
                                print(f"✗ (melhoria insuficiente: +{change})")
                
                except Exception as e:
                    if verbose:
                        print(f"✗ (erro: {str(e)})")
                    
                    # Registra erro mas continua
                    iteration_improvements.append({
                        'prompt_id': prompt_id,
                        'error': str(e),
                        'improvement': 0
                    })
            
            # 5. Regista histórico da iteração
            iteration_end_score = self.analyzer.analyze(current_text)['score']
            iteration_total_improvement = iteration_end_score - iteration_start_score
            
            history.append({
                'iteration': iteration,
                'score_before': iteration_start_score,
                'score_after': iteration_end_score,
                'improvement': iteration_total_improvement,
                'transformations_applied': iteration_improvements,
                'pipeline_size': len(pipeline)
            })
            
            if verbose:
                print(f"\n   📊 Resultado da iteração: {iteration_start_score} → {iteration_end_score} (+{iteration_total_improvement})")
        
        # Análise final
        final_diagnosis = self.analyzer.analyze(current_text)
        final_score = final_diagnosis['score']
        
        success = final_score >= target_score
        
        if verbose:
            print("\n" + "="*60)
            if success:
                print("✅ HUMANIZAÇÃO CONCLUÍDA COM SUCESSO")
            else:
                print("⚠️  HUMANIZAÇÃO PARCIAL")
            print("="*60)
            print(f"📊 Score inicial:  {original_score}/100")
            print(f"📊 Score final:    {final_score}/100")
            print(f"📈 Melhoria total: +{final_score - original_score} pontos")
            print(f"🔄 Iterações:      {iteration}")
            
            if not success:
                print(f"\n⚠️  Target ({target_score}) não atingido, mas texto melhorou")
        
        return {
            'success': success,
            'original_text': ai_text,
            'final_text': current_text,
            'original_score': original_score,
            'final_score': final_score,
            'iterations': iteration,
            'history': history,
            'message': 'Target atingido' if success else 'Target não atingido mas texto melhorado'
        }
    
    def _print_diagnosis_summary(self, diagnosis: Dict):
        """
        Imprime resumo do diagnóstico de forma legível.
        
        Args:
            diagnosis: Output do TextAnalyzer.analyze()
        """
        lex = diagnosis['lexical']
        syn = diagnosis['syntactic']
        sty = diagnosis['style']
        struct = diagnosis['structure']
        
        print("\n📝 Resumo do diagnóstico:")
        
        # Lexical
        print(f"   Léxico:")
        print(f"      - Diversidade (TTR): {lex['ttr']:.2f}")
        print(f"      - Nominalizações: {len(lex['nominalizations'])}")
        print(f"      - Marcadores IA: {len(lex['ai_markers'])}")
        
        # Syntactic
        print(f"   Sintaxe:")
        print(f"      - Variação de ritmo: {syn['std_dev_sentence_length']:.1f}")
        print(f"      - Voz passiva: {syn['passive_voice_count']}")
        
        # Style
        print(f"   Estilo:")
        print(f"      - Impessoalidade: {sty['impersonality_score']:.2f}")
        print(f"      - Formalidade: {sty['formality_score']:.2f}")
        print(f"      - Pronomes 1ª pessoa: {sty['first_person_count']}")
        
        # Structure
        print(f"   Estrutura:")
        print(f"      - Intro formulaica: {'Sim' if struct['has_formulaic_intro'] else 'Não'}")
        print(f"      - Conclusão formulaica: {'Sim' if struct['has_formulaic_conclusion'] else 'Não'}")
    
    def quick_analyze(self, text: str) -> Dict:
        """
        Análise rápida sem transformação.
        
        Args:
            text: Texto a analisar
        
        Returns:
            Dicionário com análise completa e problemas identificados
        
        Examples:
            >>> result = orchestrator.quick_analyze("Texto para analisar...")
            >>> print(f"Score: {result['score']}")
        """
        diagnosis = self.analyzer.analyze(text)
        problems = self.pipeline_gen.get_problem_summary(diagnosis)
        
        return {
            **diagnosis,
            'problems': problems
        }
    
    def test_single_transformation(
        self, 
        text: str, 
        prompt_id: str, 
        verbose: bool = True
    ) -> Dict:
        """
        Testa uma única transformação específica.
        
        Útil para debug e teste de prompts individuais.
        
        Args:
            text: Texto a transformar
            prompt_id: ID do prompt a aplicar
            verbose: Se True, imprime detalhes
        
        Returns:
            Dicionário com resultado da transformação e validação
        
        Examples:
            >>> result = orchestrator.test_single_transformation(
            ...     "O texto foi elaborado pela equipa.",
            ...     "SINTAXE_ATIVAR_VOZ"
            ... )
            >>> print(result['transformed_text'])
        """
        if verbose:
            print(f"\n🧪 Testando transformação: {prompt_id}")
            print("="*60)
        
        # Analisa texto original
        diagnosis = self.analyzer.analyze(text)
        original_score = diagnosis['score']
        
        if verbose:
            print(f"📊 Score original: {original_score}/100")
        
        # Gera parâmetros para o prompt
        pipeline = self.pipeline_gen.generate(diagnosis)
        
        # Procura prompt específico no pipeline
        params = None
        for pid, p in pipeline:
            if pid == prompt_id:
                params = p
                break
        
        # Se não encontrou no pipeline, usa parâmetros vazios/default
        if params is None:
            if verbose:
                print(f"⚠️  Prompt {prompt_id} não recomendado para este texto")
                print("   Aplicando mesmo assim com parâmetros default...")
            
            # Gera parâmetros default baseado no tipo de prompt
            params = self._get_default_params(prompt_id, diagnosis)
        
        try:
            # Constrói e executa prompt
            prompt = self.prompt_lib.build_prompt(prompt_id, text, params)
            transformed_text = self.executor.execute(prompt)
            
            # Valida
            validation = self.validator.validate(text, transformed_text)
            
            if verbose:
                print(f"\n✓ Transformação concluída")
                print(f"📊 Score após: {validation['score_after']}/100")
                print(f"📈 Melhoria: {validation['improvement']:+d} pontos")
                print(f"\n📄 Texto transformado:")
                print("-"*60)
                print(transformed_text)
                print("-"*60)
            
            return {
                'success': True,
                'original_text': text,
                'transformed_text': transformed_text,
                'validation': validation
            }
            
        except Exception as e:
            if verbose:
                print(f"\n✗ Erro: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'original_text': text
            }
    
    def _get_default_params(self, prompt_id: str, diagnosis: Dict) -> Dict:
        """
        Gera parâmetros default para um prompt baseado no diagnóstico.
        
        Args:
            prompt_id: ID do prompt
            diagnosis: Diagnóstico do texto
        
        Returns:
            Dicionário com parâmetros default
        """
        lex = diagnosis['lexical']
        syn = diagnosis['syntactic']
        sty = diagnosis['style']
        
        params_map = {
            'LEXICO_DIVERSIFICAR': {
                'ttr_atual': lex['ttr'],
                'palavras_repetidas': str(lex['repeated_words'])
            },
            'LEXICO_DESNOMINALIZAR': {
                'nominalizacoes': ', '.join(lex['nominalizations'][:10]) or 'Nenhuma'
            },
            'SINTAXE_VARIAR_RITMO': {
                'std_dev': syn['std_dev_sentence_length'],
                'avg_length': syn['avg_sentence_length']
            },
            'SINTAXE_ATIVAR_VOZ': {
                'passivas_count': syn['passive_voice_count']
            },
            'ESTILO_PESSOALIZAR': {
                'impersonality_score': sty['impersonality_score'],
                'first_person_count': sty['first_person_count']
            },
            'ESTILO_INFORMALIZAR': {
                'formality_score': sty['formality_score']
            },
            'ESTRUTURA_LIMPAR_MARCADORES': {
                'marcadores': '\n   - '.join(lex['ai_markers']) or 'Nenhum'
            },
            'ESTRUTURA_REORGANIZAR': {}
        }
        
        return params_map.get(prompt_id, {})
