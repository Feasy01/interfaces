from src.interface.config.cfg_parser import CfgParser
import json
class CfgParserJson(CfgParser):
    @staticmethod
    def parse_cfg(cfg) -> dict:
        with open(cfg) as f:
            data = json.load(f)
            return data
            