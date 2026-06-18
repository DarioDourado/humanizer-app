"""
Sistema de Humanização de Texto IA

Este pacote contém um sistema modular para transformar texto gerado por IA
em texto com características mais humanas.
"""

from .analyzer import TextAnalyzer
from .prompts import PromptLibrary
from .executor import PromptExecutor
from .validator import Validator
from .pipeline import PipelineGenerator
from .orchestrator import HumanizationOrchestrator

__version__ = "1.0.0"

__all__ = [
    'TextAnalyzer',
    'PromptLibrary',
    'PromptExecutor',
    'Validator',
    'PipelineGenerator',
    'HumanizationOrchestrator'
]
