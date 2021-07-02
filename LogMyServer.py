from podrum.console.logger import logger


class LogMyServer(logger):
    def __init__(self):
        self.dictionary: dict = {
            "on_load": "DevTools is on fire!!!",
            "on_unload": "Goodbye my friend :)",
            "load_plugin": "Loading {} plugin",
            "unload_plugin": "Unloading {}...",
            "wrong_api": "Plugin {} can't be loaded due to bad plugin API version.",
            "wrong_api2": "Plugin API version {}",
            "wrong_api3": "Required API version {}",
            "loaded_x_plugins": "Loaded {} plugins",
            "success_loading": "Successfull loaded {}"
        }
        super().__init__()

    def from_dict(self, short: str, *args):
        if short in self.dictionary:
            self.info(self.dictionary[short].format(args[0]) if len(args) != 0
                      else self.dictionary[short])
