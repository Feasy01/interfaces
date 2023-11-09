from Include.config.CfgParserJson  import CfgParserJson
import os
configuration = CfgParserJson.parse_cfg(os.path.join(os.getcwd(),'Include/config/conenction.json'))
print(configuration)