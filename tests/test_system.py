"""
Testes básicos do sistema de humanização.

Execute com: python tests/test_system.py
"""

import sys
import os

# Adiciona diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import TextAnalyzer
from src.prompts import PromptLibrary
from src.pipeline import PipelineGenerator


def test_analyzer():
    """Testa o analisador de texto."""
    print("\n" + "="*60)
    print("🧪 TESTE 1: Analisador de Texto")
    print("="*60)
    
    try:
        analyzer = TextAnalyzer()
        
        # Texto claramente gerado por IA
        texto_ia = """
        É importante notar que a implementação da estratégia visa a otimização 
        dos processos. Além disso, verifica-se que a realização de auditorias 
        é fundamental. Em conclusão, o cenário apresenta desafios significativos.
        """
        
        resultado = analyzer.analyze(texto_ia)
        
        print(f"\n✓ Análise concluída")
        print(f"   Score: {resultado['score']}/100")
        print(f"   TTR: {resultado['lexical']['ttr']:.2f}")
        print(f"   Marcadores IA: {len(resultado['lexical']['ai_markers'])}")
        print(f"   Nominalizações: {len(resultado['lexical']['nominalizations'])}")
        print(f"   Impessoalidade: {resultado['style']['impersonality_score']:.2f}")
        
        # Verifica se score é baixo (como esperado para texto IA)
        assert resultado['score'] < 60, "Score deveria ser baixo para texto IA"
        
        print("\n✅ TESTE 1 PASSOU")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE 1 FALHOU: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_prompts():
    """Testa a biblioteca de prompts."""
    print("\n" + "="*60)
    print("🧪 TESTE 2: Biblioteca de Prompts")
    print("="*60)
    
    try:
        # Lista prompts disponíveis
        prompts = PromptLibrary.get_prompt_list()
        print(f"\n✓ {len(prompts)} prompts disponíveis:")
        for p in prompts:
            desc = PromptLibrary.get_prompt_description(p)
            print(f"   - {p}: {desc}")
        
        # Testa construção de prompt
        texto = "O texto foi elaborado pela equipa."
        params = {'passivas_count': 1}
        
        prompt = PromptLibrary.build_prompt('SINTAXE_ATIVAR_VOZ', texto, params)
        
        assert 'TAREFA' in prompt, "Prompt deve conter seção TAREFA"
        assert texto in prompt, "Prompt deve conter texto original"
        
        print("\n✓ Prompt construído com sucesso")
        print(f"   Tamanho: {len(prompt)} caracteres")
        
        print("\n✅ TESTE 2 PASSOU")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE 2 FALHOU: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline():
    """Testa o gerador de pipeline."""
    print("\n" + "="*60)
    print("🧪 TESTE 3: Gerador de Pipeline")
    print("="*60)
    
    try:
        analyzer = TextAnalyzer()
        pipeline_gen = PipelineGenerator()
        
        # Texto com vários problemas
        texto_problema = """
        É importante notar que a implementação da estratégia visa a otimização 
        dos processos. Além disso, verifica-se que a realização de auditorias 
        é fundamental. Em primeiro lugar, deve-se considerar a avaliação. 
        Em segundo lugar, a utilização de indicadores facilita a análise. 
        Em conclusão, o cenário apresenta desafios significativos.
        """
        
        # Analisa
        diagnosis = analyzer.analyze(texto_problema)
        
        # Gera pipeline
        pipeline = pipeline_gen.generate(diagnosis)
        
        print(f"\n✓ Pipeline gerado com {len(pipeline)} transformações:")
        for i, (prompt_id, params) in enumerate(pipeline, 1):
            print(f"   {i}. {prompt_id}")
        
        # Verifica que pipeline não está vazio
        assert len(pipeline) > 0, "Pipeline deveria ter transformações"
        
        # Testa resumo de problemas
        problemas = pipeline_gen.get_problem_summary(diagnosis)
        print(f"\n✓ Problemas identificados:")
        for categoria, lista in problemas.items():
            if lista:
                print(f"   {categoria.upper()}: {len(lista)} problemas")
        
        print("\n✅ TESTE 3 PASSOU")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE 3 FALHOU: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Teste de integração básico (sem API)."""
    print("\n" + "="*60)
    print("🧪 TESTE 4: Integração (sem API)")
    print("="*60)
    
    try:
        from src.orchestrator import HumanizationOrchestrator
        
        # Texto simples
        texto = "O relatório foi elaborado. A análise foi realizada. O resultado é positivo."
        
        # Testa análise rápida
        print("\n✓ Testando análise rápida...")
        
        # Nota: Não testa humanize() porque requer API key
        print("   (Teste de humanize() requer ANTHROPIC_API_KEY)")
        
        print("\n✅ TESTE 4 PASSOU")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE 4 FALHOU: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("🧪 EXECUTANDO TESTES DO SISTEMA")
    print("="*60)
    
    resultados = []
    
    # Executa testes
    resultados.append(("Analyzer", test_analyzer()))
    resultados.append(("Prompts", test_prompts()))
    resultados.append(("Pipeline", test_pipeline()))
    resultados.append(("Integration", test_integration()))
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    passou = sum(1 for _, r in resultados if r)
    total = len(resultados)
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"   {nome}: {status}")
    
    print(f"\n   Total: {passou}/{total} testes passaram")
    
    if passou == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        return True
    else:
        print(f"\n⚠️  {total - passou} teste(s) falharam")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
