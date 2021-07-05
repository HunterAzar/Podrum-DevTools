import importlib
import importlib.util
import json
from podrum.version import version
from podrum.console.logger import logger
import os
from commands.makeplugin import make_plugin

# self.logger.info("Making new ZIP file")
        # shutil.make_archive(f"{name}_{plugin_version}","zip",path)
        # shutil.move(f"{name}_{plugin_version}.zip",f"plugins/{name}_{plugin_version}.zip")
        # self.logger.success("Successfully maked ZIP file")

        #self.server.managers.plugin_manager.load(f"{self.server.get_root_path()}\\..\\plugins\\{name}_{plugin_version}.zip")


class Main:
    def __init__(self):
        self.plugin_folder_path: str = os.path.join(os.getcwd(), "plugins")
        self.loaded_plugins: list = []
        self.before_msg = ""
        self.dictionary: dict = {
            "on_load": "DevTools is on fire!!!",
            "on_unload": "Goodbye my friend :)",
            "load_plugin": "Loading {} plugin",
            "unload_plugin": "Unloading {}...",
            "wrong_api": "Plugin {} can't be loaded due to bad plugin API version.",
            "wrong_api2": "Plugin API version {}",
            "wrong_api3": "Required API version {}",
            "loaded_x_plugins": "Loaded {} plugins",
            "success_loading": "Successfull loaded {}",
            "no_plugins": "There is no plugins to load"
        }
        
    def liblary(self, short: str, *args):
        if short in self.dictionary:
            self.logger.info(self.dictionary[short].format(args[0]) if len(args) != 0
                      else self.dictionary[short])
    
    def on_load(self):
        self.logger: logger = self.server.logger
        self.logger.info(self.liblary("on_load"))
        self.server.managers.command_manager.register(make_plugin(self.server))
        self.getAllFolders()

    def on_unload(self):
        self.logger.notice(self.liblary("on_unload"))

    def toxic_load(self, path: str) -> int:
        plugin_info: dict = json.load(open(os.path.join(path, "info.json"), 'r'))
        name = plugin_info["name"]
        file_name, class_name = plugin_info["main"].rsplit(".", 1)
        plugin_version = plugin_info["version"]
        if plugin_info["name"] in self.loaded_plugins:
            return 0
        self.logger.notice(self.liblary("load_plugin", name))
        #########        Section       #########
        # CHECKING DECLARED PLUGIN API VERSION #
        ########################################
        if plugin_info["api_version"] != version.podrum_api_version:
            self.logger.warn(self.liblary("wrong_api", name))
            self.logger.warn(self.liblary("wrong_api2", plugin_version))
            self.logger.warn(self.liblary("wrong_api3", version.podrum_api_version))
            return 1
        #########        Section       #########
        # CHECKING IF PLUGIN IS ALREADY LOADED #
        ########################################
        if plugin_info["name"] in self.server.managers.plugin_manager.plugins:
            self.logger.info(self.liblary("unload_plugin", name))
            del self.server.managers.plugin_manager.plugins[plugin_info["name"]]
        #########      Section     #########
        #IMPORTING MAIN CLASS FROM PLUGIN  #
        ####################################
        spec = importlib.util.spec_from_file_location(f"{class_name}", f"{path}\{file_name}.py")
        prev_main_class = spec.loader.load_module(spec.name)
        main_class = getattr(prev_main_class,class_name)
        #########        Section        #########
        # REGISTERING PLUGIN AND INJECTING INFO #
        #########################################
        self.server.managers.plugin_manager.plugins[plugin_info["name"]] = main_class()
        self.server.managers.plugin_manager.plugins[plugin_info["name"]].name = name
        self.server.managers.plugin_manager.plugins[plugin_info["name"]].server = self.server
        self.server.managers.plugin_manager.plugins[plugin_info["name"]].path = path
        self.server.managers.plugin_manager.plugins[plugin_info["name"]].version = plugin_info["version"]
        self.server.managers.plugin_manager.plugins[plugin_info["name"]].description = plugin_info["description"]
        self.server.managers.plugin_manager.plugins[plugin_info["name"]].author = plugin_info["author"]
        self.server.managers.plugin_manager.plugins[plugin_info["name"]].devtools = "true"
        if hasattr(main_class, "on_load"):
            self.server.managers.plugin_manager.plugins[plugin_info["name"]].on_load()
        self.logger.success(self.liblary("success_loading", name))
        return 0

    def getAllFolders(self) -> None:
        howMuch = 0
        for dirs in os.listdir(self.plugin_folder_path):
            if os.path.isdir(os.path.join(self.plugin_folder_path, dirs)):
                if dirs != "DevTools":
                    self.logger.info(f"Loading {os.path.join(self.plugin_folder_path, dirs)} plugin")
                    if self.toxic_load(os.path.join(self.plugin_folder_path, dirs)) == 0:
                        howMuch = howMuch+1
        if howMuch != 0:
            self.logger.info(self.liblary("loaded_x_plugins", howMuch))
        else:
            self.logger.info(self.liblary("no_plugins"))
