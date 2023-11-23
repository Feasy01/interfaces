from src.manager.tester_manager import TesterManager
# configuration = CfgParserJson.parse_cfg(os.path.join(os.getcwd(),'Include/config/conenction.json'))
manager = TesterManager('./src/config/connections-inverted.json')
manager.write_can("can-1",(256,2,3,4,12,21,21,21,21,21,23,23,23,23,23))
manager.read_spi("MEMORY_devie_1",16)