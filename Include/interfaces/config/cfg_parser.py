from abc import ABC, abstractmethod
import os
class CfgParser(ABC):
    @staticmethod
    @abstractmethod
    def parse_cfg(cfg: str | os.PathLike) -> dict:
        """logic that parses cfg from given path to a dictionary"""
        pass
