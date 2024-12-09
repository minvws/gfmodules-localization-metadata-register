from typing import Any, TypeVar


class RepositoryBase:
    def __init__(self, db_session: Any):
        self.db_session = db_session


TRepositoryBase = TypeVar("TRepositoryBase", bound=RepositoryBase, covariant=True)
