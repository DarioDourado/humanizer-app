"""
Configurações globais do sistema de humanização de texto.
"""

import os


class Config:
    """
    Configurações centralizadas do sistema.
    
    Todas as constantes e parâmetros configuráveis devem ser definidos aqui.
    """
    
    # ========== API ==========
    
    # Chave de API da Anthropic (lê de variável ambiente)
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    
    # Modelo Claude padrão a usar
    DEFAULT_MODEL = "claude-sonnet-4-20250514"
    
    # Limite de tokens na resposta
    MAX_TOKENS = 4000
    
    # Temperatura (criatividade) - 0 a 1
    TEMPERATURE = 1.0
    
    
    # ========== ANÁLISE ==========
    
    # Modelo spaCy para análise linguística
    SPACY_MODEL = "pt_core_news_lg"
    
    
    # ========== PIPELINE ==========
    
    # Score objetivo padrão (0-100)
    TARGET_SCORE_DEFAULT = 70
    
    # Número máximo de iterações padrão
    MAX_ITERATIONS_DEFAULT = 5
    
    
    # ========== THRESHOLDS ==========
    
    # Thresholds para decisão de transformações
    # (podem ser ajustados empiricamente após testes)
    THRESHOLDS = {
        # Léxico
        'ttr_min': 0.45,                # Type-Token Ratio mínimo
        'nominalizations_max': 3,       # Número máximo de nominalizações
        'ai_markers_max': 2,            # Número máximo de marcadores IA
        
        # Sintaxe
        'burstiness_min': 3.0,          # Desvio-padrão mínimo de comprimento de frases
        'passive_voice_max': 5,         # Número máximo de construções passivas
        
        # Estilo
        'impersonality_max': 0.7,       # Score máximo de impessoalidade (0-1)
        'formality_max': 0.75,          # Score máximo de formalidade (0-1)
        'hedging_max': 5,               # Número máximo de termos hedging
        'first_person_min': 1,          # Mínimo de pronomes 1ª pessoa
        
        # Estrutura
        'transition_markers_max': 3     # Número máximo de marcadores de transição
    }
    
    
    # ========== PESOS PARA SCORE GLOBAL ==========
    
    # Pesos para cálculo do score de humanização (devem somar próximo de 1.0)
    SCORE_WEIGHTS = {
        'lexical_diversity': 0.15,      # 15% - Diversidade lexical (TTR)
        'burstiness': 0.15,             # 15% - Variação de ritmo
        'impersonality': 0.20,          # 20% - Impessoalidade
        'formality': 0.10,              # 10% - Formalidade
        'ai_markers': 0.20,             # 20% - Marcadores típicos de IA
        'nominalizations': 0.10,        # 10% - Nominalizações
        'hedging': 0.10                 # 10% - Termos de hedging
    }
    
    
    # ========== VALIDAÇÃO ==========
    
    # Melhoria mínima em pontos para considerar transformação bem-sucedida
    MIN_IMPROVEMENT = 3
    
    # Score mínimo para considerar texto "humanizado"
    MIN_HUMANIZED_SCORE = 60
    
    
    # ========== PATHS ==========
    
    # Diretório base do projeto
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Diretório de dados
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # Diretório de testes
    TESTS_DIR = os.path.join(BASE_DIR, 'tests')
    
    
    # ========== LOGGING ==========
    
    # Nível de verbosidade padrão
    VERBOSE_DEFAULT = True
    
    # Formato de log
    LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
    
    
    @classmethod
    def validate(cls) -> bool:
        """
        Valida se configurações estão corretas.
        
        Returns:
            True se configurações válidas, False caso contrário
        """
        # Verifica se API key está configurada
        if not cls.ANTHROPIC_API_KEY:
            print("⚠️  ANTHROPIC_API_KEY não configurada")
            print("   Configure com: export ANTHROPIC_API_KEY='sua-chave'")
            return False
        
        # Verifica se thresholds são válidos
        if not all(isinstance(v, (int, float)) for v in cls.THRESHOLDS.values()):
            print("⚠️  Thresholds inválidos")
            return False
        
        # Verifica se pesos somam aproximadamente 1.0
        total_weight = sum(cls.SCORE_WEIGHTS.values())
        if not (0.95 <= total_weight <= 1.05):
            print(f"⚠️  Pesos não somam 1.0 (soma atual: {total_weight})")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """Imprime configurações atuais de forma legível."""
        print("\n" + "="*60)
        print("⚙️  CONFIGURAÇÕES DO SISTEMA")
        print("="*60)
        
        print("\n📡 API:")
        print(f"   Modelo: {cls.DEFAULT_MODEL}")
        print(f"   Max tokens: {cls.MAX_TOKENS}")
        print(f"   API key configurada: {'Sim' if cls.ANTHROPIC_API_KEY else 'Não'}")
        
        print("\n📊 Análise:")
        print(f"   Modelo spaCy: {cls.SPACY_MODEL}")
        
        print("\n🎯 Pipeline:")
        print(f"   Target score padrão: {cls.TARGET_SCORE_DEFAULT}")
        print(f"   Max iterações padrão: {cls.MAX_ITERATIONS_DEFAULT}")
        
        print("\n📏 Thresholds:")
        for key, value in cls.THRESHOLDS.items():
            print(f"   {key}: {value}")
        
        print("\n⚖️  Pesos do score:")
        for key, value in cls.SCORE_WEIGHTS.items():
            print(f"   {key}: {value:.0%}")
        
        print("\n" + "="*60)


# Singleton para acesso global
config = Config()
