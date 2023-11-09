from Include.config.CfgParserJson  import CfgParserJson
from Include.factory.tester_serializer import ControllerFactory
import os
# configuration = CfgParserJson.parse_cfg(os.path.join(os.getcwd(),'Include/config/conenction.json'))
a = ControllerFactory(CfgParserJson.parse_cfg(os.path.join(os.getcwd(),'Include/config/conenction.json')))