# 📋 DOCUMENTAÇÃO TÉCNICA COMPLETA

## Sistema de Humanização de Texto IA v1.0

---

## 🎯 Visão Geral

Sistema Python modular que transforma texto gerado por IA em texto com características humanas através de análise linguística e transformações iterativas guiadas por prompts especializados.



---

## 📦 Módulos Detalhados

### 1. analyzer.py - TextAnalyzer

**Responsabilidade**: Análise linguística completa do texto

**Classe Principal**: `TextAnalyzer`

**Inicialização**:
```python
analyzer = TextAnalyzer(model="pt_core_news_lg")
```

**Método Principal**: `analyze(text: str) -> dict`

**Output**:
```python
{
    'lexical': {
        'ttr': float,                    # Type-Token Ratio
        'mtld': float,                   # Lexical Diversity
        'repeated_words': dict,          # Palavras repetidas
        'nominalizations': list,         # Substantivos abstratos
        'ai_markers': list,              # Expressões típicas IA
        'unique_words_ratio': float      # Proporção palavras únicas
    },
    'syntactic': {
        'avg_sentence_length': float,         # Média palavras/frase
        'std_dev_sentence_length': float,     # Desvio-padrão (burstiness)
        'passive_voice_count': int,           # Construções passivas
        'syntactic_depth': float,             # Profundidade sintática
        'svo_ratio': float                    # Proporção ordem SVO
    },
    'style': {
        'impersonality_score': float,    # 0-1 (maior = mais impessoal)
        'formality_score': float,        # 0-1 (maior = mais formal)
        'hedging_count': int,            # Termos de cautela
        'first_person_count': int,       # Pronomes 1ª pessoa
        'exclamation_count': int,        # Exclamações
        'ellipsis_count': int            # Reticências
    },
    'structure': {
        'has_formulaic_intro': bool,         # Introdução formulaica
        'has_formulaic_conclusion': bool,    # Conclusão formulaica
        'transition_markers': int,           # Marcadores de transição
        'paragraph_count': int,              # Número de parágrafos
        'avg_paragraph_length': float        # Frases por parágrafo
    },
    'score': int  # Score global 0-100
}
```

**Cálculo do Score**:
```python
score = (
    ttr_score * 0.15 +                    # Diversidade lexical
    burstiness_score * 0.15 +             # Variação de ritmo
    (1 - impersonality) * 0.20 +          # Pessoalidade
    (1 - formality) * 0.10 +              # Informalidade
    ai_markers_score * 0.20 +             # Falta de marcadores IA
    nominalizations_score * 0.10 +        # Poucas nominalizações
    hedging_score * 0.10 +                # Hedging moderado
    bonus - penalties                      # Ajustes
)
```

---

### 2. prompts.py - PromptLibrary

**Responsabilidade**: Armazenamento e construção de prompts especializados

**Classe Principal**: `PromptLibrary`

**Método Principal**: `build_prompt(prompt_id: str, text: str, params: dict) -> str`

**Prompts Disponíveis**:

| ID | Parâmetros Necessários | Objetivo |
|----|------------------------|----------|
| `LEXICO_DIVERSIFICAR` | `ttr_atual`, `palavras_repetidas` | ↑ Diversidade vocabular |
| `LEXICO_DESNOMINALIZAR` | `nominalizacoes` | ↓ Substantivos abstratos |
| `SINTAXE_VARIAR_RITMO` | `std_dev`, `avg_length` | ↑ Variação comprimento frases |
| `SINTAXE_ATIVAR_VOZ` | `passivas_count` | Passiva → Ativa |
| `ESTILO_PESSOALIZAR` | `impersonality_score`, `first_person_count` | ↑ Voz pessoal |
| `ESTILO_INFORMALIZAR` | `formality_score` | ↓ Formalidade |
| `ESTRUTURA_LIMPAR_MARCADORES` | `marcadores` | ✗ Expressões-fórmula |
| `ESTRUTURA_REORGANIZAR` | (nenhum) | ⚡ Quebrar estrutura rígida |

**Exemplo de Uso**:
```python
prompt = PromptLibrary.build_prompt(
    'SINTAXE_ATIVAR_VOZ',
    'O relatório foi elaborado.',
    {'passivas_count': 1}
)
```

---

### 3. executor.py - PromptExecutor

**Responsabilidade**: Comunicação com Claude API

**Classe Principal**: `PromptExecutor`

**Inicialização**:
```python
executor = PromptExecutor(api_key="sk-ant-...")
# Ou deixa ler de ANTHROPIC_API_KEY
executor = PromptExecutor()
```

**Método Principal**: `execute(prompt: str, model: str, max_tokens: int) -> str`

**Configuração API**:
```python
api_url = "https://api.anthropic.com/v1/messages"
headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01"
}
```

**Handling de Erros**:
- `ValueError`: API key não fornecida
- `requests.exceptions.Timeout`: Timeout (>60s)
- `Exception`: Erro da API (status != 200)

---

### 4. validator.py - Validator

**Responsabilidade**: Validação de melhorias

**Classe Principal**: `Validator(analyzer)`

**Método Principal**: `validate(original: str, transformed: str) -> dict`

**Output**:
```python
{
    'improved': bool,              # Melhorou ≥3 pontos?
    'score_before': int,           # Score original
    'score_after': int,            # Score transformado
    'improvement': int,            # Diferença
    'recommendation': str,         # Próximo passo
    'analysis_before': dict,       # Análise completa original
    'analysis_after': dict         # Análise completa transformado
}
```

**Recomendações**:
- `'success'`: Score ≥60, pode parar
- `'continue_pipeline'`: Melhorou mas <60, continuar
- `'transformation_failed'`: Melhoria <3 pontos, tentar outra

**Método Auxiliar**: `get_improvement_summary(validation: dict) -> str`

---

### 5. pipeline.py - PipelineGenerator

**Responsabilidade**: Decisão de transformações a aplicar

**Classe Principal**: `PipelineGenerator(thresholds: dict)`

**Thresholds Padrão**:
```python
THRESHOLDS = {
    'ttr_min': 0.45,
    'nominalizations_max': 3,
    'burstiness_min': 3.0,
    'passive_voice_max': 5,
    'impersonality_max': 0.7,
    'formality_max': 0.75,
    'ai_markers_max': 2
}
```

**Método Principal**: `generate(diagnosis: dict) -> list[tuple]`

**Output**: Lista ordenada por prioridade
```python
[
    ('LEXICO_DIVERSIFICAR', {'ttr_atual': 0.32, ...}),
    ('SINTAXE_VARIAR_RITMO', {'std_dev': 1.8, ...}),
    ...
]
```

**Ordem de Prioridade**:
1. Léxico (diversidade, nominalizações)
2. Sintaxe (ritmo, voz passiva)
3. Estilo (impessoalidade, formalidade)
4. Estrutura (marcadores, organização)

**Métodos Auxiliares**:
- `generate_prioritized(diagnosis, max_transformations)`: Limita pipeline
- `get_problem_summary(diagnosis)`: Resumo de problemas
- `should_continue(diagnosis, target_score)`: Verifica se deve continuar

---

### 6. orchestrator.py - HumanizationOrchestrator

**Responsabilidade**: Coordenação do processo completo

**Classe Principal**: `HumanizationOrchestrator(api_key, spacy_model)`

**Componentes Internos**:
```python
self.analyzer = TextAnalyzer()
self.pipeline_gen = PipelineGenerator()
self.executor = PromptExecutor()
self.validator = Validator()
self.prompt_lib = PromptLibrary()
```

**Método Principal**: `humanize(ai_text, target_score, max_iterations, verbose) -> dict`

**Algoritmo**:
```
1. Analisa texto inicial → score_inicial
2. LOOP (até max_iterations):
   a. Diagnóstica texto atual
   b. Se score >= target: RETORNA sucesso
   c. Gera pipeline de transformações
   d. Para cada transformação:
      - Constrói prompt
      - Executa via API
      - Valida melhoria
      - Se melhorou: aceita transformação
   e. Regista histórico
3. RETORNA resultado (sucesso ou parcial)
```

**Output**:
```python
{
    'success': bool,
    'original_text': str,
    'final_text': str,
    'original_score': int,
    'final_score': int,
    'iterations': int,
    'history': [
        {
            'iteration': int,
            'score_before': int,
            'score_after': int,
            'improvement': int,
            'transformations_applied': [...]
        },
        ...
    ],
    'message': str
}
```

**Métodos Auxiliares**:
- `quick_analyze(text)`: Análise sem transformação
- `test_single_transformation(text, prompt_id)`: Testa prompt individual
- `_print_diagnosis_summary(diagnosis)`: Output legível

---

### 7. utils.py - Funções Auxiliares

**Funções Principais**:

```python
# Carregar dados
load_json_data(filename) -> dict

# Detecção lexical
detect_nominalizations(text) -> list[str]
calculate_type_token_ratio(tokens) -> float
calculate_mtld(tokens) -> float
count_repeated_words(tokens, min_count) -> dict

# Detecção sintática
detect_passive_voice(doc) -> int

# Detecção de estilo
detect_first_person_pronouns(text) -> int
detect_hedging_terms(text, hedging_list) -> int
detect_ai_markers(text, markers_list) -> list[str]

# Detecção de estrutura
detect_formulaic_intro(text) -> bool
detect_formulaic_conclusion(text) -> bool
count_transition_markers(text) -> int
```

---

## 🔧 Configuração (config.py)

### Constantes Principais

```python
# API
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
DEFAULT_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4000
TEMPERATURE = 1.0

# Análise
SPACY_MODEL = "pt_core_news_lg"

# Pipeline
TARGET_SCORE_DEFAULT = 70
MAX_ITERATIONS_DEFAULT = 5

# Thresholds (ver pipeline.py)
# Score Weights (ver analyzer.py)
```

### Métodos

```python
Config.validate() -> bool        # Valida configurações
Config.print_config()           # Imprime configurações
```

---

## 📊 Fluxo de Dados

### Input → Output

```
Texto IA
    ↓
[Analyzer] → diagnosis
    ↓
[PipelineGenerator] → pipeline [(prompt_id, params), ...]
    ↓
[Loop] Para cada (prompt_id, params):
    ↓
    [PromptLibrary] → prompt completo
    ↓
    [Executor] → texto transformado
    ↓
    [Validator] → validação
    ↓
    Se melhorou: aceita texto
    ↓
[Orchestrator] → resultado final
```

### Ciclo de Melhoria

```
Score 25 → Análise → Pipeline [A, B, C]
    ↓
Aplica A → Score 32 (+7) ✓
    ↓
Aplica B → Score 35 (+3) ✓
    ↓
Aplica C → Score 38 (+3) ✓
    ↓
Nova iteração → Nova análise → Pipeline [D, E]
    ↓
...continua até target ou max_iterations
```

---

## 🎯 Casos de Uso

### 1. Uso Básico
```python
orchestrator = HumanizationOrchestrator(api_key="...")
result = orchestrator.humanize("Texto IA...")
```

### 2. Análise Diagnóstica
```python
analysis = orchestrator.quick_analyze("Texto...")
print(f"Score: {analysis['score']}")
print(f"Problemas: {analysis['problems']}")
```

### 3. Teste de Prompt Específico
```python
result = orchestrator.test_single_transformation(
    text="...",
    prompt_id="SINTAXE_ATIVAR_VOZ"
)
```

### 4. Batch Processing
```python
textos = ["texto1", "texto2", "texto3"]
resultados = [orchestrator.humanize(t) for t in textos]
```

### 5. Pipeline Personalizado
```python
analyzer = TextAnalyzer()
generator = PipelineGenerator(thresholds={...})

diagnosis = analyzer.analyze(text)
pipeline = generator.generate(diagnosis)
# Aplicar manualmente cada transformação
```

---

## 🐛 Tratamento de Erros

### Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `OSError: Modelo não encontrado` | spaCy não instalado | `python -m spacy download pt_core_news_lg` |
| `ValueError: API key not provided` | Sem ANTHROPIC_API_KEY | `export ANTHROPIC_API_KEY='...'` |
| `requests.exceptions.Timeout` | API demorou >60s | Reduzir tamanho do texto |
| `Exception: API error 429` | Rate limit | Aguardar ou reduzir frequência |
| `KeyError: parâmetro não fornecido` | Params faltando no prompt | Verificar params necessários |

### Try-Catch Recomendado

```python
try:
    result = orchestrator.humanize(text)
except ValueError as e:
    print(f"Configuração inválida: {e}")
except requests.exceptions.RequestException as e:
    print(f"Erro de rede: {e}")
except Exception as e:
    print(f"Erro geral: {e}")
```

---

## 📈 Performance e Limites

### Tempo de Execução Estimado

- **Análise**: ~1-2s (spaCy)
- **Transformação única**: ~3-5s (Claude API)
- **Iteração completa**: ~15-30s (3-5 transformações)
- **Processo total**: ~1-3 min (3-5 iterações)

### Limites

- **Tamanho de texto**: ~1000-2000 palavras por transformação
- **API tokens**: 4000 tokens por request (configurável)
- **Rate limits**: Depende do plano Anthropic
- **Memória**: ~500MB (modelo spaCy)

### Otimizações

- Cache de análises spaCy
- Batch de textos pequenos
- Paralelização de análises (múltiplos textos)
- Ajuste de thresholds para reduzir iterações



## 📚 Referências

- **spaCy**: https://spacy.io/
- **Anthropic Claude**: https://www.anthropic.com/
- **Type-Token Ratio**: https://en.wikipedia.org/wiki/Lexical_diversity
- **Heylighen F-score**: Heylighen, F. & Dewaele, J.M. (2002)

---

## 📝 Notas de Versão

### v1.0.0 (Atual)

**Features**:
- ✅ Análise linguística completa (4 categorias)
- ✅ 8 prompts especializados
- ✅ Pipeline inteligente com thresholds
- ✅ Validação iterativa
- ✅ Score 0-100 multidimensional
- ✅ Histórico detalhado
- ✅ Configuração flexível

**Limitações Conhecidas**:
- Apenas português
- Requer API key paga
- Score 100 é teoricamente impossível de atingir
- Textos muito curtos (<50 palavras) têm análise menos confiável

---

**Documentação mantida por**: Sistema de Humanização de Texto IA v1.0
**Última atualização**: Implementação completa do sistema
