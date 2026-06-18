"""
Executor de prompts via Claude API (Anthropic).

Este módulo encapsula a comunicação com a API da Anthropic para executar
prompts de transformação de texto.
"""

import requests
import os
from typing import Optional


class PromptExecutor:
    """
    Executor que envia prompts para Claude API e retorna texto transformado.
    
    Attributes:
        api_key: Chave de API da Anthropic
        api_url: URL do endpoint da API
        default_model: Modelo Claude padrão a usar
        default_max_tokens: Limite padrão de tokens
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa executor com credenciais da API.
        
        Args:
            api_key: Chave de API da Anthropic. Se None, tenta ler de ANTHROPIC_API_KEY
        
        Raises:
            ValueError: Se API key não for fornecida nem encontrada em variável ambiente
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "API key da Anthropic não fornecida. "
                "Forneça via parâmetro ou configure variável ambiente ANTHROPIC_API_KEY"
            )
        
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.default_model = "claude-sonnet-4-20250514"
        self.default_max_tokens = 4000
    
    def execute(
        self, 
        prompt: str, 
        model: Optional[str] = None, 
        max_tokens: Optional[int] = None,
        temperature: float = 1.0
    ) -> str:
        """
        Executa prompt via Claude API e retorna resposta.
        
        Args:
            prompt: Prompt completo a executar
            model: Modelo Claude a usar (padrão: claude-sonnet-4-20250514)
            max_tokens: Limite de tokens na resposta (padrão: 4000)
            temperature: Criatividade da resposta 0-1 (padrão: 1.0)
        
        Returns:
            Texto transformado retornado pelo Claude
        
        Raises:
            requests.exceptions.RequestException: Se houver erro de rede
            Exception: Se API retornar erro
        
        Examples:
            >>> executor = PromptExecutor(api_key="sk-...")
            >>> prompt = "Reescreve: O texto foi elaborado."
            >>> result = executor.execute(prompt)
            >>> print(result)
            'Elaborámos o texto.'
        """
        # Usa valores padrão se não fornecidos
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens
        
        # Prepara headers
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Prepara payload
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            # Faz request
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=payload,
                timeout=60  # Timeout de 60 segundos
            )
            
            # Verifica status
            if response.status_code != 200:
                error_detail = self._parse_error(response)
                raise Exception(
                    f"Erro da API Claude (status {response.status_code}): {error_detail}"
                )
            
            # Extrai texto da resposta
            response_data = response.json()
            
            # Valida estrutura da resposta
            if 'content' not in response_data or not response_data['content']:
                raise Exception(
                    "Resposta da API não contém campo 'content'"
                )
            
            # Extrai texto (primeiro bloco de conteúdo)
            text_content = response_data['content'][0]['text']
            
            return text_content
            
        except requests.exceptions.Timeout:
            raise Exception(
                "Timeout ao comunicar com API Claude (>60s). "
                "Tente novamente ou reduza o tamanho do texto."
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro de rede ao comunicar com API Claude: {str(e)}")
    
    def _parse_error(self, response: requests.Response) -> str:
        """
        Extrai mensagem de erro detalhada da resposta da API.
        
        Args:
            response: Objeto Response com erro
        
        Returns:
            Mensagem de erro formatada
        """
        try:
            error_data = response.json()
            
            # Tenta extrair diferentes formatos de erro
            if 'error' in error_data:
                error_obj = error_data['error']
                
                if isinstance(error_obj, dict):
                    error_type = error_obj.get('type', 'unknown')
                    error_message = error_obj.get('message', 'Sem detalhes')
                    return f"{error_type}: {error_message}"
                else:
                    return str(error_obj)
            
            return response.text
            
        except Exception:
            # Se não conseguir parsear, retorna texto bruto
            return response.text
    
    def test_connection(self) -> bool:
        """
        Testa se a conexão com a API está funcional.
        
        Returns:
            True se conexão OK, False caso contrário
        
        Examples:
            >>> executor = PromptExecutor(api_key="sk-...")
            >>> if executor.test_connection():
            ...     print("API OK")
            ... else:
            ...     print("Erro na API")
        """
        try:
            test_prompt = "Responde apenas: OK"
            response = self.execute(test_prompt, max_tokens=10)
            return len(response) > 0
        except Exception:
            return False
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estima número de tokens num texto (aproximação).
        
        Regra aproximada: 1 token ≈ 4 caracteres em português
        
        Args:
            text: Texto a estimar
        
        Returns:
            Número estimado de tokens
        
        Note:
            Esta é uma estimativa grosseira. Para contagem exata,
            use a biblioteca oficial da Anthropic (anthropic.count_tokens)
        """
        return len(text) // 4
