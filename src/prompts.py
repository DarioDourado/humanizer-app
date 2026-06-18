"""
Biblioteca otimizada de prompts para humanização de texto gerado por IA.

Ordem de aplicação recomendada (pipeline):
1. ESTRUTURA_REORGANIZAR - Remove estrutura escolar
2. ESTRUTURA_LIMPAR_MARCADORES - Elimina frases-fórmula  
3. SINTAXE_VARIAR_COMPRIMENTO - Varia tamanho de frases
4. SINTAXE_VARIAR_COMPLEXIDADE - Alterna subordinação simples/complexa
5. SINTAXE_ENRIQUECER_PONTUACAO - Adiciona ponto e vírgula, travessões
6. SINTAXE_ATIVAR_VOZ - Converte passiva em ativa
7. LEXICO_DESNOMINALIZAR - Substitui substantivos por verbos
8. LEXICO_DIVERSIFICAR_SELETIVO - Varia apenas palavras comuns repetidas
9. DENSIDADE_CRIAR_PICOS - Distribui informação desigualmente
10. ESTILO_PESSOALIZAR - Adiciona voz humana
11. ESTILO_INFORMALIZAR - Reduz formalidade
12. ADICIONAR_DIGRESSOES - Insere apartes naturais
13. ADICIONAR_METALINGUISTICA - Comentários sobre escolhas
14. ADICIONAR_IMPERFEICOES - Imperfeições estratégicas
"""

from typing import Dict, List
import json
import os


def load_json_data(file_path: str) -> dict:
    """Carrega dados de um arquivo JSON."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


class PromptLibrary:
    """Biblioteca de prompts de transformação linguística."""
    
    def __init__(self, prompts_file: str = None):
        """Inicializa biblioteca carregando prompts do arquivo JSON."""
        if prompts_file is None:
            # Get the directory of this file and build path to data/prompts.json
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            prompts_file = os.path.join(project_root, 'data', 'prompts.json')
        self.prompts = load_json_data(prompts_file)
    
    def get_prompt(self, prompt_id: str) -> str:
        """
        Obtém template de prompt pelo ID.
        
        Args:
            prompt_id: ID do prompt (ex: 'SINTAXE_VARIAR_COMPRIMENTO')
        
        Returns:
            Template do prompt
        
        Raises:
            ValueError: Se prompt_id não existir
        """
        for category in self.prompts.values():
            for prompt in category:
                if prompt['id'] == prompt_id:
                    return prompt['template']
        
        raise ValueError(f"Prompt ID '{prompt_id}' não encontrado")
    
    def get_prompt_description(self, prompt_id: str) -> str:
        """
        Obtém descrição de um prompt pelo ID.
        
        Args:
            prompt_id: ID do prompt
        
        Returns:
            Descrição do prompt
        
        Raises:
            ValueError: Se prompt_id não existir
        """
        for category in self.prompts.values():
            for prompt in category:
                if prompt['id'] == prompt_id:
                    return prompt.get('description', prompt.get('nome', prompt_id))
        
        raise ValueError(f"Prompt ID '{prompt_id}' não encontrado")
    
    def get_all_prompt_ids(self) -> List[str]:
        """
        Obtém lista de todos os IDs de prompts disponíveis.
        
        Returns:
            Lista de IDs de prompts
        """
        prompt_ids = []
        for category in self.prompts.values():
            for prompt in category:
                prompt_ids.append(prompt['id'])
        return prompt_ids
    
    def get_prompts_by_category(self, category: str) -> List[Dict]:
        """
        Obtém todos os prompts de uma categoria.
        
        Args:
            category: Nome da categoria (ex: 'sintaxe', 'lexico')
        
        Returns:
            Lista de prompts da categoria
        
        Raises:
            ValueError: Se categoria não existir
        """
        if category not in self.prompts:
            raise ValueError(f"Categoria '{category}' não encontrada")
        
        return self.prompts[category]

    # ============================================================
    # METADADOS E ORDEM DE PIPELINE
    # ============================================================
    
    PIPELINE_ORDER = [
        'ESTRUTURA_REORGANIZAR',
        'ESTRUTURA_LIMPAR_MARCADORES',
        'SINTAXE_VARIAR_COMPRIMENTO',
        'SINTAXE_VARIAR_COMPLEXIDADE',
        'SINTAXE_ENRIQUECER_PONTUACAO',
        'SINTAXE_ATIVAR_VOZ',
        'LEXICO_DESNOMINALIZAR',
        'LEXICO_DIVERSIFICAR_SELETIVO',
        'DENSIDADE_CRIAR_PICOS',
        'ESTILO_PESSOALIZAR',
        'ESTILO_INFORMALIZAR',
        'ADICIONAR_DIGRESSOES',
        'ADICIONAR_METALINGUISTICA',
        'ADICIONAR_IMPERFEICOES'
    ]
    
    # Pipelines por intensidade
    PIPELINES = {
        'LEVE': [
            'ESTRUTURA_LIMPAR_MARCADORES',
            'SINTAXE_ATIVAR_VOZ',
            'ESTILO_INFORMALIZAR'
        ],
        
        'MEDIO': [
            'ESTRUTURA_REORGANIZAR',
            'ESTRUTURA_LIMPAR_MARCADORES',
            'SINTAXE_VARIAR_COMPRIMENTO',
            'SINTAXE_ATIVAR_VOZ',
            'LEXICO_DESNOMINALIZAR',
            'ESTILO_PESSOALIZAR'
        ],
        
        'COMPLETO': PIPELINE_ORDER
    }
    
    PROMPT_DESCRIPTIONS = {
        'ESTRUTURA_REORGANIZAR': 'Remove estrutura escolar (intro-corpo-conclusão)',
        'ESTRUTURA_LIMPAR_MARCADORES': 'Elimina frases-fórmula de IA',
        'SINTAXE_VARIAR_COMPRIMENTO': 'Cria variação dramática no tamanho de frases',
        'SINTAXE_VARIAR_COMPLEXIDADE': 'Alterna frases simples com muito complexas',
        'SINTAXE_ENRIQUECER_PONTUACAO': 'Adiciona ponto e vírgula, travessões, parênteses',
        'SINTAXE_ATIVAR_VOZ': 'Converte voz passiva em ativa',
        'LEXICO_DESNOMINALIZAR': 'Substitui substantivos por verbos',
        'LEXICO_DIVERSIFICAR_SELETIVO': 'Varia palavras comuns (preserva técnicas)',
        'DENSIDADE_CRIAR_PICOS': 'Distribui informação desigualmente',
        'ESTILO_PESSOALIZAR': 'Adiciona voz humana e pronomes pessoais',
        'ESTILO_INFORMALIZAR': 'Reduz formalidade excessiva',
        'ADICIONAR_DIGRESSOES': 'Insere apartes/comentários laterais',
        'ADICIONAR_METALINGUISTICA': 'Adiciona comentários sobre escolhas',
        'ADICIONAR_IMPERFEICOES': 'Imperfeições estratégicas (começar com E/Mas)'
    }
    
    def build_prompt(self, prompt_id: str, text: str, params: Dict = None) -> str:
        """
        Constrói prompt com parâmetros preenchidos.
        
        Args:
            prompt_id: ID do prompt (ex: 'SINTAXE_VARIAR_COMPRIMENTO')
            text: Texto a transformar
            params: Dicionário com métricas (opcional para alguns prompts)
        
        Returns:
            String do prompt completo
        """
        # Get the prompt template from loaded JSON data
        prompt_template = self.get_prompt(prompt_id)
        
        # Parâmetros padrão caso não sejam fornecidos
        default_params = {
            'texto': text,  # Changed from 'text' to 'texto' to match JSON templates
            'std_dev': 0,
            'avg_length': 0,
            'ttr_atual': 0,
            'palavras_repetidas': '{}',
            'nominalizacoes': '[]',
            'passivas_count': 0,
            'impersonality_score': 0,
            'first_person_count': 0,
            'formality_score': 0,
            'marcadores': '[]',
            'semicolon_count': 0,
            'dash_count': 0,
            'colon_count': 0,
            'parentheses_count': 0
        }
        
        # Merge parâmetros fornecidos com defaults
        if params:
            default_params.update(params)
        
        try:
            return prompt_template.format(**default_params)
        except KeyError as e:
            raise KeyError(
                f"Parâmetro {e} necessário para prompt '{prompt_id}'"
            )
    
    @staticmethod
    def get_pipeline_order(intensity: str = 'COMPLETO') -> list:
        """
        Retorna ordem recomendada de aplicação dos prompts.
        
        Args:
            intensity: 'LEVE', 'MEDIO' ou 'COMPLETO'
        """
        return PromptLibrary.PIPELINES.get(intensity, PromptLibrary.PIPELINE_ORDER).copy()
    
    @staticmethod
    def get_description(prompt_id: str) -> str:
        """Retorna descrição breve de um prompt."""
        return PromptLibrary.PROMPT_DESCRIPTIONS.get(
            prompt_id, 
            'Descrição não disponível'
        )
