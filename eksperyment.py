from include.config.CfgParserJson  import CfgParserJson
from include.factory.tester_serializer import ControllerFactory
from include.manager.tester_manager import TesterManager
import os
# configuration = CfgParserJson.parse_cfg(os.path.join(os.getcwd(),'Include/config/conenction.json'))
manager = TesterManager(os.path.join(os.getcwd(),'include/config/conenction.json'))