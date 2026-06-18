#!/bin/bash

# Script de setup rápido do Sistema de Humanização de Texto IA
# Execute com: bash setup.sh

echo "================================================"
echo "🚀 SETUP: Sistema de Humanização de Texto IA"
echo "================================================"
echo ""

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+"
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"
echo ""

# Cria ambiente virtual (opcional)
read -p "Criar ambiente virtual? (recomendado) [Y/n]: " create_venv
create_venv=${create_venv:-Y}

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo ""
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    
    echo "✓ Ambiente virtual criado"
    echo ""
    echo "⚠️  Para ativar o ambiente virtual:"
    echo "   source venv/bin/activate  (Linux/Mac)"
    echo "   venv\\Scripts\\activate     (Windows)"
    echo ""
    
    # Ativa ambiente virtual
    source venv/bin/activate 2>/dev/null || . venv/bin/activate
fi

# Instala dependências
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependências instaladas"
else
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

echo ""

# Instala modelo spaCy
echo "📦 Instalando modelo spaCy (pt_core_news_lg)..."
echo "   (Isso pode demorar alguns minutos...)"
python3 -m spacy download pt_core_news_lg

if [ $? -eq 0 ]; then
    echo "✓ Modelo spaCy instalado"
else
    echo "❌ Erro ao instalar modelo spaCy"
    echo "   Tente manualmente: python -m spacy download pt_core_news_lg"
fi

echo ""

# Configura .env
if [ ! -f .env ]; then
    echo "📝 Configurando variáveis de ambiente..."
    read -p "Tem chave de API da Anthropic? [Y/n]: " has_key
    has_key=${has_key:-Y}
    
    if [[ $has_key =~ ^[Yy]$ ]]; then
        read -p "Cole sua ANTHROPIC_API_KEY: " api_key
        echo "ANTHROPIC_API_KEY=$api_key" > .env
        echo "✓ .env criado"
    else
        cp .env.example .env
        echo "⚠️  .env criado a partir de template"
        echo "   Edite .env e adicione sua ANTHROPIC_API_KEY"
    fi
else
    echo "✓ .env já existe"
fi

echo ""
echo "================================================"
echo "✅ SETUP CONCLUÍDO!"
echo "================================================"
echo ""
echo "📚 Próximos passos:"
echo ""
echo "1. Configure sua API key (se ainda não fez):"
echo "   export ANTHROPIC_API_KEY='sua-chave'"
echo "   Ou edite o ficheiro .env"
echo ""
echo "2. Teste o sistema:"
echo "   python tests/test_system.py"
echo ""
echo "3. Execute o exemplo:"
echo "   python example.py"
echo ""
echo "4. Consulte o README.md para mais informações"
echo ""
echo "================================================"
