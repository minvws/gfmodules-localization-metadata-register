from typing import Type, Dict, Any

from app.db.repository import RepositoryBase
from app.db.models import Base

repository_registry: Dict[Type[Base], Type[RepositoryBase]] = {}


def repository(model_class: Type[Base]) -> Any:
    def decorator(repo_class: Type[RepositoryBase]) -> Type[RepositoryBase]:
        """
        Decorator to register a repository for a model class

        :param repo_class:
        :return:
        """
        if model_class in repository_registry:
            raise ValueError(f"A repository for '{model_class}' is already registered.")

        repository_registry[model_class] = repo_class
        return repo_class
    return decorator
