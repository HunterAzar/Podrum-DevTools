import importlib
import importlib.util
import json
from podrum.version import version
from podrum.console.logger import logger
import os
from commands.makeplugin import make_plugin
from threading import Timer
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from podrum.server import server
    from podrum.plugin_manager import plugin_manager


class Main:
    def __init__(self) -> None:
        self.plugin_folder_path: str = os.path.join(os.getcwd(), "plugins")
        self.loaded_plugins: dict = {}
        self.before_msg = "[ DevTools ] >> "
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
            "no_plugins": "There is no plugins to load",
            "start_fake_reload": "Started fake reloading",
            "success_fake_reload": "Successfull reloaded all plugins",
            "dict_fake_reload": "Plugin not found skipped (working but with error xD)"
        }
        self.server: 'server'
        self.plugin_manager: 'plugin_manager'

    def on_reload(self) -> None:
        self.liblary("start_fake_reload")
        for plugin in self.loaded_plugins.copy():
            try:
                if plugin == "!DevTools":
                    continue
                if hasattr(self.plugin_manager.plugins[plugin], "on_unload"):
                    self.plugin_manager.plugins[plugin].on_unload()

                del self.plugin_manager.plugins[plugin]
                self.liblary("unload_plugin", plugin)
            except:
                self.liblary("dict_fake_reload")
        self.liblary("success_fake_reload")

    def liblary(self, short: str, *args) -> None:
        if short in self.dictionary:
            self.logger.info(self.before_msg + (self.dictionary[short].format(args[0]) if len(args) != 0
                                                else self.dictionary[short]))

    def make_me_first(self) -> None:
        old_plugin_list: dict = self.plugin_manager.plugins
        new_plugin_list: dict = self.loaded_plugins
        for plugin in old_plugin_list:
            if plugin == "DevTools":
                continue
            self.logger.info(plugin)
            new_plugin_list[old_plugin_list[plugin].name] = old_plugin_list[plugin]
        self.plugin_manager.plugins = new_plugin_list

    def on_load(self) -> None:
        self.loaded_plugins["!DevTools"] = self
        self.logger: logger = self.server.logger
        self.logger.info(self.liblary("on_load"))
        self.plugin_manager = self.server.managers.plugin_manager
        self.server.managers.command_manager.register(make_plugin(self.server))
        Timer(0.3, self.getAllFolders).start()

    def on_unload(self) -> None:
        self.on_reload()
        self.logger.notice(self.liblary("on_unload"))

    def toxic_load(self, path: str) -> int:
        plugin_info: dict = json.load(
            open(os.path.join(path, "info.json"), 'r'))
        name = plugin_info["name"]
        file_name, class_name = plugin_info["main"].rsplit(".", 1)
        plugin_version = plugin_info["version"]
        if name in self.loaded_plugins:
            return 0
        self.logger.notice(self.liblary("load_plugin", name))
        #########        Section       #########
        # CHECKING DECLARED PLUGIN API VERSION #
        ########################################
        if plugin_info["api_version"] != version.podrum_api_version:
            self.logger.warn(self.liblary("wrong_api", name))
            self.logger.warn(self.liblary("wrong_api2", plugin_version))
            self.logger.warn(self.liblary(
                "wrong_api3", version.podrum_api_version))
            return 1
        #########        Section       #########
        # CHECKING IF PLUGIN IS ALREADY LOADED #
        ########################################
        if name in self.plugin_manager.plugins:
            self.logger.info(self.liblary("unload_plugin", name))
            del self.plugin_manager.plugins[name]
        #########      Section     #########
        #IMPORTING MAIN CLASS FROM PLUGIN  #
        ####################################
        spec = importlib.util.spec_from_file_location(
            f"{class_name}", f"{path}\{file_name}.py")
        prev_main_class = spec.loader.load_module(spec.name)
        main_class = getattr(prev_main_class, class_name)
        #########        Section        #########
        # REGISTERING PLUGIN AND INJECTING INFO #
        #########################################
        self.plugin_manager.plugins[name] = main_class()
        self.plugin_manager.plugins[name].name = name
        self.plugin_manager.plugins[name].server = self.server
        self.plugin_manager.plugins[name].path = path
        self.plugin_manager.plugins[name].version = plugin_info["version"]
        self.plugin_manager.plugins[name].description = plugin_info["description"]
        self.plugin_manager.plugins[name].author = plugin_info["author"]
        self.plugin_manager.plugins[name].devtools = "true"
        if hasattr(main_class, "on_load"):
            self.plugin_manager.plugins[name].on_load()
        self.logger.success(self.liblary("success_loading", name))
        self.loaded_plugins[name] = self.plugin_manager.plugins[name]
        return 0

    def getAllFolders(self) -> None:
        howMuch = 0
        for dirs in os.listdir(self.plugin_folder_path):
            if os.path.isdir(os.path.join(self.plugin_folder_path, dirs)):
                if dirs != "DevTools":
                    self.logger.info(
                        f"Loading {os.path.join(self.plugin_folder_path, dirs)} plugin")
                    if self.toxic_load(os.path.join(self.plugin_folder_path, dirs)) == 0:
                        howMuch = howMuch+1
        if howMuch != 0:
            self.logger.info(self.liblary("loaded_x_plugins", howMuch))
        else:
            self.logger.info(self.liblary("no_plugins"))
        self.make_me_first()
