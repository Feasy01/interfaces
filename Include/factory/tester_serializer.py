from ..controllers.DigitalDIscoveryMultiplex import DigitalDiscoveryMultiplex
class ControllerFactory:
    def __init__(self,cfg:dict) -> None:
        self._cfg = cfg
        self.controller_factory_from_cfg()
        pass




    def controller_factory_from_cfg(self):
        dut_dict = {}
        for x in self._cfg.keys():
            class_name,instance_vars = self._cfg[x].popitem()
            # disct =instance_vars
            instance = globals()[class_name](**instance_vars)
            print(instance)
            try:
                class_name,instance_vars = self._cfg[x].popitem()
                # print(class_name,instance_vars)
                if class_name in globals():
                    disct =instance_vars
                    instance = globals()[class_name](instance_vars)
                    print(instance)
                    # dut_dict[x] = instance
            except Exception:
                print('empty key')
        print(dut_dict)
            # print(self._cfg[x])
