"""CLI Commands"""
from .deploy import deploy
from .migrate import migrate
from .test import test
from .task import task
from .ask import ask

__all__ = ['deploy', 'migrate', 'test', 'task', 'ask']
