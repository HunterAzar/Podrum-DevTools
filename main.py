import importlib
import importlib.util
import json
from podrum.version import version
from podrum.console.logger import logger
import os
from commands.makeplugin import make_plugin
from threading import Timer
from typing import TYPE_CHECKING
import shutil as zip
if TYPE_CHECKING:
    from podrum.server import server
    from podrum.plugin_manager import plugin_manager


class Main:
    def __init__(self) -> None:
        self.plugin_folder_path: str = os.path.join(os.getcwd(), "plugins")
        if not os.path.exists(f"{self.plugin_folder_path}/DevTools_Plugins"):
            os.makedirs(f"{self.plugin_folder_path}/DevTools_Plugins")

        self.loaded_plugins: dict = {}
        self.before_msg = "[ DevTools ] >> "
        self.server: 'server'
        self.plugin_manager: 'plugin_manager'

    def on_load(self) -> None:
        self.plugin_manager = self.server.managers.plugin_manager
        self.logger: logger = self.server.logger
        self.logger.info("DevTools is working!!!")
        self.server.managers.command_manager.register(make_plugin(self.server))
        self.getAllFolders()

    def on_unload(self) -> None:
        self.logger.notice(self.before_msg+" Bye")

    def toxic_load(self, path: str) -> int:
        try:
            plugin_info: dict = json.load(
                open(os.path.join(path, "info.json"), 'r'))
        except:
            print("not a plugin")
            return 1
        name = plugin_info["name"]
        if name in self.plugin_manager.plugins:
            self.logger.info(f"Already loaded {name}")
            return 1
        print(name)
        print(self.plugin_manager.plugins)
        if(name=="DevTools"): return 1
        plugin_version = plugin_info["version"]
        if name in self.loaded_plugins:
            return 1
        self.logger.info("lol")
        if plugin_info["api_version"] != version.podrum_api_version:
            self.logger.warn("Wrong API!!!")
            self.logger.warn(f"You are using {plugin_version}")
            self.logger.warn(f"But we support {version.podrum_api_version}")
            return 1
        
        
        zip.make_archive(f"{plugin_info['name']}_{plugin_info['version']}","zip",path)

        if(os.path.exists(f"{self.plugin_folder_path}\\DevTools_Plugins\\{plugin_info['name']}_{plugin_info['version']}.zip")):
            os.remove(f"{self.plugin_folder_path}\\DevTools_Plugins\\{plugin_info['name']}_{plugin_info['version']}.zip")

        zip.move(f"{plugin_info['name']}_{plugin_info['version']}.zip",
                 f"{self.plugin_folder_path}\\DevTools_Plugins")
        return 0

    def getAllFolders(self) -> None:
        howMuch = 0
        print("6")
        for dirs in os.listdir(self.plugin_folder_path):
            print("5")
            if os.path.isdir(os.path.join(self.plugin_folder_path, dirs)):
                print("4")
                if dirs != "Podrum-DevTools":
                    print("2")
                    print(dirs)
                    if self.toxic_load(os.path.join(self.plugin_folder_path, dirs)) == 0:
                        howMuch = howMuch+1
                        print("1")
                else:
                    print("3")
            print("7")
        print("8")
        if howMuch != 0:
            self.logger.info(f"Loaded {howMuch} plugins")
