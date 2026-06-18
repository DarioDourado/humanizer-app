"""
Script de exemplo de uso do sistema de humanização.

Este script demonstra como usar o HumanizationOrchestrator para
transformar texto gerado por IA em texto mais humano.
"""

import os
from dotenv import load_dotenv 
from src.orchestrator import HumanizationOrchestrator


def main():
    load_dotenv() 
    
    """Exemplo de uso do sistema de humanização."""
    
    print("\n" + "="*80)
    print("🤖 SISTEMA DE HUMANIZAÇÃO DE TEXTO IA")
    print("="*80)
    
    # Ler texto do ficheiro input.txt
    input_file = "input.txt"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            texto_ia = f.read().strip()
        print(f"\n📂 Texto carregado de: {input_file}")
    except FileNotFoundError:
        print(f"\n⚠️  ERRO: Ficheiro '{input_file}' não encontrado!")
        print("Crie o ficheiro 'input.txt' com o texto que quer humanizar.")
        return
    
    print("\n📄 TEXTO ORIGINAL (gerado por IA):")
    print("-"*80)
    print(texto_ia)
    print("-"*80)
    
    # Verifica se API key está configurada
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("\n⚠️  ERRO: ANTHROPIC_API_KEY não configurada!")
        print("\nPara usar este sistema, configure sua API key:")
        print("   export ANTHROPIC_API_KEY='sua-chave-aqui'")
        print("\nOu execute:")
        print("   ANTHROPIC_API_KEY='sua-chave' python example.py")
        return
    
    try:
        # Inicializa o orquestrador
        print("\n🔧 Inicializando sistema...")
        orchestrator = HumanizationOrchestrator(api_key=api_key)
        
        # Executa humanização
        print("\n🚀 Iniciando processo de humanização...\n")
        
        resultado = orchestrator.humanize(
            ai_text=texto_ia,
            target_score=70,      # Score objetivo
            max_iterations=5,     # Máximo de iterações
            verbose=True          # Mostra progresso detalhado
        )
        
        # Mostra resultado final
        print("\n" + "="*80)
        print("📊 RESULTADO FINAL")
        print("="*80)
        
        print(f"\n✓ Sucesso: {'Sim' if resultado['success'] else 'Parcial'}")
        print(f"📈 Score inicial:  {resultado['original_score']}/100")
        print(f"📈 Score final:    {resultado['final_score']}/100")
        print(f"📈 Melhoria:       +{resultado['final_score'] - resultado['original_score']} pontos")
        print(f"🔄 Iterações:      {resultado['iterations']}")
        
        print("\n📄 TEXTO HUMANIZADO:")
        print("-"*80)
        print(resultado['final_text'])
        print("-"*80)
        
        # Histórico de transformações
        if resultado['history']:
            print("\n📜 HISTÓRICO DE TRANSFORMAÇÕES:")
            for entry in resultado['history']:
                iter_num = entry['iteration']
                improvement = entry['improvement']
                print(f"\n   Iteração {iter_num}: {entry['score_before']} → {entry['score_after']} (+{improvement})")
                
                for trans in entry['transformations_applied']:
                    if 'error' not in trans:
                        print(f"      ✓ {trans['prompt_id']}: +{trans['improvement']} pontos")
                    else:
                        print(f"      ✗ {trans['prompt_id']}: erro")
        
        # Gravar texto humanizado em output.txt
        output_file = "output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("TEXTO HUMANIZADO\n")
            f.write("="*80 + "\n\n")
            f.write(f"Score inicial:  {resultado['original_score']}/100\n")
            f.write(f"Score final:    {resultado['final_score']}/100\n")
            f.write(f"Melhoria:       +{resultado['final_score'] - resultado['original_score']} pontos\n")
            f.write(f"Iterações:      {resultado['iterations']}\n\n")
            f.write("-"*80 + "\n")
            f.write(resultado['final_text'])
            f.write("\n" + "-"*80 + "\n")
        
        print(f"\n💾 Texto humanizado gravado em: {output_file}")
        
        print("\n" + "="*80)
        print("✅ PROCESSO CONCLUÍDO")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
