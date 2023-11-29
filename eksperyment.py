from src.manager.tester_manager import TesterManager
import asyncio
# configuration = CfgParserJson.parse_cfg(os.path.join(os.getcwd(),'Include/config/conenction.json'))
def test_mock_spi():
    manager = TesterManager('./src/config/demo-setup.json')
    results = manager.spy_spi("demo-spi",20000)
    results2 = manager.spy_spi("demo-spi2",20000)

    return(results.result(),results2.result())    # bingbong = manager.send_command("Rpi","arp -a")
    # await asyncio.gather(results,res)
    # has to be async
# manager.send_command("spidev_test")
# asyncio.run(test_mock_spi())
print(test_mock_spi())