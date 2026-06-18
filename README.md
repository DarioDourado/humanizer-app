# Sistema de Humanização de Texto IA

Sistema Python modular que analisa texto gerado por IA e o transforma automaticamente para parecer escrito por humano. Usa análise linguística (spaCy) para diagnosticar problemas, aplica prompts especializados via Claude API para corrigir cada problema, e valida iterativamente até atingir um score objetivo.

## 📋 Características

- **Análise Multidimensional**: 4 categorias de métricas (lexical, sintática, estilo, estrutura)
- **8 Prompts Especializados**: Cada um focado num aspecto específico da humanização
- **Pipeline Inteligente**: Decide automaticamente que transformações aplicar
- **Validação Iterativa**: Verifica melhoria após cada transformação
- **Score 0-100**: Métrica objetiva de quão "humano" o texto parece

## 🏗️ Arquitetura

```
humanizer-app/
├── src/
│   ├── __init__.py
│   ├── analyzer.py          # Análise linguística completa (spaCy)
│   ├── prompts.py           # 8 prompts especializados
│   ├── executor.py          # Executor Claude API
│   ├── validator.py         # Validação de melhorias
│   ├── pipeline.py          # Gerador de pipeline de transformações
│   ├── orchestrator.py      # Coordenador principal
│   └── utils.py             # Funções auxiliares
├── data/
│   ├── ai_markers.json      # Expressões típicas de IA
│   ├── hedging_terms.json   # Termos de cautela
│   └── nominalizations.json # Padrões de nominalização
├── tests/
│   └── test_system.py       # Testes básicos
├── config.py                # Configurações globais
├── requirements.txt         # Dependências
├── example.py              # Script de exemplo
└── README.md               # Este ficheiro
```

## 🚀 Instalação

### 1. Requisitos

- Python 3.8+
- Conta Anthropic (para API key)

### 2. Instalar dependências

```bash
cd humanizer-app
pip install -r requirements.txt
```

### 3. Instalar modelo spaCy

```bash
python -m spacy download pt_core_news_lg
```

### 4. Configurar API key

```bash
export ANTHROPIC_API_KEY='sua-chave-anthropic'
```

Ou crie ficheiro `.env`:
```
ANTHROPIC_API_KEY=sua-chave-anthropic
```

## 💡 Uso Básico

### Exemplo Simples

```python
from src.orchestrator import HumanizationOrchestrator

# Texto gerado por IA
texto_ia = """
É importante notar que a implementação da estratégia visa a otimização dos processos. 
Além disso, verifica-se uma tendência crescente na adoção de tecnologias. 
Em suma, o cenário apresenta desafios significativos e oportunidades vastas.
"""

# Inicializa sistema
orchestrator = HumanizationOrchestrator(api_key="sua-chave")

# Humaniza
resultado = orchestrator.humanize(
    ai_text=texto_ia,
    target_score=70,
    verbose=True
)

# Resultado
print(f"Score: {resultado['original_score']} → {resultado['final_score']}")
print(f"Texto humanizado:\n{resultado['final_text']}")
```

### Executar Script de Exemplo

```bash
python example.py
```

## 📊 Sistema de Scoring

O score vai de **0 a 100**:

- **0-30**: Muito claramente IA
- **31-50**: Provavelmente IA
- **51-70**: Ambíguo / Melhorado mas ainda com padrões IA
- **71-90**: Provavelmente humano
- **91-100**: Muito provavelmente humano

### Componentes do Score

| Métrica | Peso | Descrição |
|---------|------|-----------|
| Diversidade Lexical | 15% | Type-Token Ratio (TTR) |
| Burstiness | 15% | Variação do comprimento de frases |
| Impessoalidade | 20% | Falta de voz pessoal |
| Formalidade | 10% | Nível de linguagem formal |
| Marcadores IA | 20% | Expressões-fórmula típicas |
| Nominalizações | 10% | Substantivos abstratos excessivos |
| Hedging | 10% | Termos de cautela/incerteza |

## 🔧 Prompts Especializados

### 1. LEXICO_DIVERSIFICAR
Aumenta diversidade vocabular, substitui palavras repetidas

### 2. LEXICO_DESNOMINALIZAR
Transforma substantivos abstratos em verbos ativos

### 3. SINTAXE_VARIAR_RITMO
Cria ritmo variado alternando frases curtas e longas

### 4. SINTAXE_ATIVAR_VOZ
Converte voz passiva em voz ativa

### 5. ESTILO_PESSOALIZAR
Adiciona pronomes pessoais e voz humana

### 6. ESTILO_INFORMALIZAR
Reduz formalidade excessiva

### 7. ESTRUTURA_LIMPAR_MARCADORES
Remove expressões-fórmula típicas de IA

### 8. ESTRUTURA_REORGANIZAR
Quebra estrutura académica rígida (intro-dev-conclusão)

## 🔬 Uso Avançado

### Análise Rápida (sem transformação)

```python
resultado = orchestrator.quick_analyze("Texto para analisar...")
print(f"Score: {resultado['score']}")
print(f"Problemas: {resultado['problems']}")
```

### Testar Prompt Individual

```python
resultado = orchestrator.test_single_transformation(
    text="O relatório foi elaborado pela equipa.",
    prompt_id="SINTAXE_ATIVAR_VOZ",
    verbose=True
)
```

### Personalizar Thresholds

```python
from src.pipeline import PipelineGenerator

custom_thresholds = {
    'ttr_min': 0.50,           # Mais exigente
    'formality_max': 0.70      # Menos formal
}

pipeline_gen = PipelineGenerator(thresholds=custom_thresholds)
```

## 🧪 Testes

```bash
python -m pytest tests/
```

Ou teste manualmente:

```bash
python tests/test_system.py
```

## ⚙️ Configuração

Edite [config.py](config.py) para ajustar:

- **Target score padrão**: `TARGET_SCORE_DEFAULT = 70`
- **Max iterações**: `MAX_ITERATIONS_DEFAULT = 5`
- **Thresholds**: Dicionário `THRESHOLDS`
- **Pesos do score**: Dicionário `SCORE_WEIGHTS`

## 📝 Métricas Detalhadas

### Métricas Lexicais
- **TTR** (Type-Token Ratio): Diversidade vocabular
- **MTLD**: Diversidade lexical robusta
- **Nominalizações**: Substantivos abstratos (-ção, -mento, etc.)
- **Marcadores IA**: Expressões-fórmula típicas

### Métricas Sintáticas
- **Comprimento médio de frases**
- **Desvio-padrão** (burstiness): Variação de ritmo
- **Voz passiva**: Contagem de construções passivas
- **Profundidade sintática**: Complexidade das frases

### Métricas de Estilo
- **Impessoalidade**: Falta de pronomes pessoais
- **Formalidade**: F-score de Heylighen
- **Hedging**: Termos de cautela
- **Elementos emocionais**: Exclamações, reticências

### Métricas de Estrutura
- **Introdução formulaica**: "Neste texto...", "É importante..."
- **Conclusão formulaica**: "Em conclusão...", "Em suma..."
- **Marcadores de transição**: "Além disso", "Por outro lado"

## 🐛 Troubleshooting

### Erro: Modelo spaCy não encontrado
```bash
python -m spacy download pt_core_news_lg
```

### Erro: API key não configurada
```bash
export ANTHROPIC_API_KEY='sua-chave'
```

### Erro: Timeout na API
- Texto muito longo: divida em partes menores
- Reduza `MAX_TOKENS` em [config.py](config.py)

### Score não melhora
- Aumente `max_iterations`
- Verifique se texto já é relativamente humano (score inicial >60)
- Ajuste thresholds no [config.py](config.py)

## 📚 Estrutura dos Dados

### ai_markers.json
Lista de expressões típicas de texto gerado por IA:
```json
{
  "markers": [
    "é importante notar que",
    "em conclusão",
    "verifica-se que",
    ...
  ]
}
```

### hedging_terms.json
Termos de cautela/incerteza:
```json
{
  "terms": [
    "geralmente",
    "tende a",
    "provavelmente",
    ...
  ]
}
```

### nominalizations.json
Sufixos e exemplos de nominalização:
```json
{
  "suffixes": ["ção", "mento", "ância", ...],
  "common_examples": ["implementação", "avaliação", ...]
}
```

## 🤝 Contribuir

1. Fork o projeto
2. Crie branch para feature (`git checkout -b feature/MinhaFeature`)
3. Commit mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para branch (`git push origin feature/MinhaFeature`)
5. Abra Pull Request

## 📄 Licença

Este projeto é para uso educacional e de pesquisa.

## 🔗 Recursos

- [spaCy](https://spacy.io/) - Biblioteca de NLP
- [Anthropic Claude API](https://www.anthropic.com/api) - API de IA
- [Documentação spaCy PT](https://spacy.io/models/pt) - Modelos portugueses

## 👤 Autor

Sistema desenvolvido como solução modular para humanização de texto gerado por IA.

## 📊 Status do Projeto

✅ **Versão 1.0** - Sistema completo e funcional

### Features Implementadas
- ✅ Análise linguística completa
- ✅ 8 prompts especializados
- ✅ Pipeline inteligente
- ✅ Validação iterativa
- ✅ Sistema de scoring robusto
- ✅ Configuração flexível

### Roadmap Futuro
- [ ] Interface web (Streamlit/Gradio)
- [ ] Suporte para outros idiomas
- [ ] Cache de transformações
- [ ] Métricas avançadas (perplexity, etc.)
- [ ] Fine-tuning de thresholds automático
- [ ] Batch processing de múltiplos textos

---

**Happy Humanizing! 🤖→👤**
