import importlib
import importlib.util
import json
import sys
from podrum.plugin_manager import plugin_manager
from podrum.version import version
from podrum.server import server
from podrum.console.logger import logger
import os
import shutil

class Main:
    def __init__(self):
        self.plugin_folder_path: str = os.path.join(os.getcwd(), "plugins")
        self.loaded_plugins: list = []
        
    def on_load(self):
        self.server.logger.info("DevTools is on fire!!!")
        self.getAllFolders()

    def on_unload(self):
        self.logger.notice("Goodbye my friend :)")

    def toxic_load(self,path:str) -> int:
        plugin_info: dict = json.load(open(os.path.join(path, "info.json"), 'r'))
        name = plugin_info["name"]
        file_name, class_name = plugin_info["main"].rsplit(".", 1)
        plugin_version = plugin_info["version"]
        if plugin_info["name"] in self.loaded_plugins:
            return 0
        self.server.logger.notice(f"Getting plugin {name} infos...")
        if plugin_info["api_version"] != version.podrum_api_version:
            self.server.logger.warn(f"""Plugin {plugin_info["name"]} can't be loaded due to bad plugin API version. """)
            self.server.logger.warn(f"""Plugin API version {plugin_info["api_version"]}""")
            self.server.logger.warn(f"Required API version {version.podrum_api_version}")
            return 1
        if plugin_info["name"] in self.server.managers.plugin_manager.plugins:
            self.server.logger.info("Unloading stage 1/1 ...")
            del self.server.managers.plugin_manager.plugins[plugin_info["name"]]
        # self.logger.info("Making new ZIP file")
        # shutil.make_archive(f"{name}_{plugin_version}","zip",path)
        # shutil.move(f"{name}_{plugin_version}.zip",f"plugins/{name}_{plugin_version}.zip")
        # self.logger.success("Successfully maked ZIP file")
        self.server.logger.info("Server please load this plugin now...")
        #self.server.managers.plugin_manager.load(f"{self.server.get_root_path()}\\..\\plugins\\{name}_{plugin_version}.zip")
        spec = importlib.util.spec_from_file_location(f"{class_name}", f"{path}\{file_name}.py")
        prev_main_class = spec.loader.load_module(spec.name)
        main_class = getattr(prev_main_class,class_name)
        self.server.managers.plugin_manager.plugins[plugin_info["name"]] = main_class()
        self.server.managers.plugin_manager.plugins[plugin_info["name"]].server = self.server
        self.server.managers.plugin_manager.plugins[plugin_info["name"]].path = path
        self.server.managers.plugin_manager.plugins[plugin_info["name"]].version = plugin_info["version"]
        self.server.managers.plugin_manager.plugins[plugin_info["name"]].description = plugin_info["description"]
        self.server.managers.plugin_manager.plugins[plugin_info["name"]].author = plugin_info["author"]
        if(hasattr(main_class, "on_load")):
            self.server.managers.plugin_manager.plugins[plugin_info["name"]].on_load()
        self.server.logger.success(f"""Thank you server for loading {plugin_info["name"]}""")
        return 0

    def getAllFolders(self) -> None:
        howMuch = 0
        for dirs in os.listdir(self.plugin_folder_path):
            if os.path.isdir(os.path.join(self.plugin_folder_path, dirs)):
                if(dirs != "DevTools"):
                    self.server.logger.info(f"Loading {os.path.join(self.plugin_folder_path, dirs)} plugin")
                    if(self.toxic_load(os.path.join(self.plugin_folder_path, dirs)) == 0):
                        howMuch = howMuch+1
        if howMuch != 0:
            self.server.logger.info(f"Loaded {howMuch} plugins")
        else:
            self.server.logger.info("There is no plugins to load")
