# 🚀 Guia de Início Rápido

## Instalação em 3 Passos

### 1️⃣ Setup Automático (Recomendado)

```bash
cd humanizer-app
bash setup.sh
```

O script irá:
- ✓ Verificar Python
- ✓ Criar ambiente virtual (opcional)
- ✓ Instalar dependências
- ✓ Instalar modelo spaCy
- ✓ Configurar API key

### 2️⃣ Setup Manual

```bash
# Instalar dependências
pip install -r requirements.txt

# Instalar modelo spaCy
python -m spacy download pt_core_news_lg

# Configurar API key
export ANTHROPIC_API_KEY='sua-chave'
```

### 3️⃣ Verificar Instalação

```bash
python tests/test_system.py
```

## 💻 Uso Básico - 5 Linhas de Código

```python
from src.orchestrator import HumanizationOrchestrator

orchestrator = HumanizationOrchestrator(api_key="sua-chave")
resultado = orchestrator.humanize("É importante notar que...")

print(resultado['final_text'])
print(f"Score: {resultado['final_score']}/100")
```

## 📊 Exemplo Completo

```python
from src.orchestrator import HumanizationOrchestrator

# Texto típico de IA
texto_ia = """
É importante notar que a implementação da estratégia visa a otimização 
dos processos organizacionais. Além disso, verifica-se uma tendência 
crescente na adoção de tecnologias verdes. Em conclusão, o cenário 
apresenta desafios significativos e oportunidades vastas.
"""

# Inicializar sistema
orchestrator = HumanizationOrchestrator(api_key="sua-chave")

# Humanizar
resultado = orchestrator.humanize(
    ai_text=texto_ia,
    target_score=70,        # Score objetivo
    max_iterations=5,       # Máximo de tentativas
    verbose=True            # Mostrar progresso
)

# Verificar resultado
if resultado['success']:
    print("✅ Objetivo atingido!")
    print(f"📈 {resultado['original_score']} → {resultado['final_score']}")
    print(f"\n📄 Texto humanizado:\n{resultado['final_text']}")
else:
    print("⚠️  Melhorou mas não atingiu target")
    print(f"Score: {resultado['final_score']}/100")
```

## 🔧 Casos de Uso

### 1. Análise Rápida (Sem Transformação)

```python
resultado = orchestrator.quick_analyze("Seu texto aqui...")
print(f"Score: {resultado['score']}/100")
print(f"Problemas: {resultado['problems']}")
```

### 2. Testar Transformação Específica

```python
resultado = orchestrator.test_single_transformation(
    text="O relatório foi elaborado pela equipa.",
    prompt_id="SINTAXE_ATIVAR_VOZ"
)
print(resultado['transformed_text'])
# Output: "A equipa elaborou o relatório."
```

### 3. Pipeline Personalizado

```python
from src.analyzer import TextAnalyzer
from src.pipeline import PipelineGenerator

analyzer = TextAnalyzer()
pipeline_gen = PipelineGenerator()

diagnosis = analyzer.analyze("Seu texto...")
pipeline = pipeline_gen.generate(diagnosis)

for prompt_id, params in pipeline:
    print(f"Aplicar: {prompt_id}")
```

## 📋 Prompts Disponíveis

| ID | Descrição |
|----|-----------|
| `LEXICO_DIVERSIFICAR` | Aumenta diversidade vocabular |
| `LEXICO_DESNOMINALIZAR` | Reduz substantivos abstratos |
| `SINTAXE_VARIAR_RITMO` | Varia comprimento de frases |
| `SINTAXE_ATIVAR_VOZ` | Converte voz passiva em ativa |
| `ESTILO_PESSOALIZAR` | Adiciona voz pessoal |
| `ESTILO_INFORMALIZAR` | Reduz formalidade |
| `ESTRUTURA_LIMPAR_MARCADORES` | Remove expressões-fórmula IA |
| `ESTRUTURA_REORGANIZAR` | Quebra estrutura académica |

## ⚙️ Configuração Rápida

### Alterar Target Score
```python
resultado = orchestrator.humanize(texto, target_score=80)  # Mais exigente
```

### Mais Iterações
```python
resultado = orchestrator.humanize(texto, max_iterations=10)
```

### Modo Silencioso
```python
resultado = orchestrator.humanize(texto, verbose=False)
```

### Thresholds Personalizados
```python
from src.pipeline import PipelineGenerator

custom = PipelineGenerator(thresholds={
    'ttr_min': 0.50,      # Mais exigente
    'formality_max': 0.70  # Menos formal
})
```

## 🐛 Troubleshooting Rápido

### ❌ "Modelo spaCy não encontrado"
```bash
python -m spacy download pt_core_news_lg
```

### ❌ "API key não configurada"
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### ❌ "ModuleNotFoundError"
```bash
# Se estiver noutro diretório
export PYTHONPATH=/caminho/para/humanizer-app:$PYTHONPATH
```

### ❌ Timeout na API
- Divida texto em partes menores
- Ou reduza max_tokens em config.py

## 📊 Interpretar Resultados

### Scores
- **0-30**: Claramente IA ❌
- **31-50**: Provavelmente IA ⚠️
- **51-70**: Ambíguo 🤔
- **71-90**: Provavelmente humano ✅
- **91-100**: Muito humano ✅✅

### Histórico
```python
for entry in resultado['history']:
    print(f"Iteração {entry['iteration']}: +{entry['improvement']} pontos")
    for trans in entry['transformations_applied']:
        print(f"  - {trans['prompt_id']}: +{trans['improvement']}")
```

## 📚 Próximos Passos

1. **Ler README completo**: [README.md](README.md)
2. **Experimentar**: Rode `python example.py`
3. **Personalizar**: Edite [config.py](config.py)
4. **Integrar**: Use no seu projeto

## 💡 Dicas

- ✅ Textos entre 100-500 palavras funcionam melhor
- ✅ Score inicial <40 tem mais margem de melhoria
- ✅ Use `verbose=True` para debug
- ✅ Target 70 é bom equilíbrio (humano mas não perfeito)
- ⚠️ Textos muito curtos (<50 palavras) são difíceis de analisar
- ⚠️ Score >80 pode ser difícil de atingir automaticamente

## 🆘 Suporte

- **Documentação completa**: [README.md](README.md)
- **Testes**: `python tests/test_system.py`
- **Exemplo funcional**: `python example.py`

---

**Pronto para humanizar! 🤖→👤**
