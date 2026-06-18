# Sistema de Humanização de Texto IA

Sistema Python modular que analisa texto gerado por IA e o transforma automaticamente para parecer escrito por humano. Usa análise linguística (spaCy) para diagnosticar problemas, aplica prompts especializados via Claude API para corrigir cada problema, e valida iterativamente até atingir um score objetivo.

## 📋 Características

- **Análise Multidimensional**: 4 categorias de métricas (lexical, sintática, estilo, estrutura)
- **8 Prompts Especializados**: Cada um focado num aspecto específico da humanização
- **Pipeline Inteligente**: Decide automaticamente que transformações aplicar
- **Validação Iterativa**: Verifica melhoria após cada transformação
- **Score 0-100**: Métrica objetiva de quão "humano" o texto parece


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

