from podrum.console.logger import logger
import os
import json

class Devplugins:
    def __init__(self, server: object) -> None:
        self.plugin_folder_path = os.path.join(os.getcwd(), "plugins")
        self.server: object = server
        self.logger: logger = self.server.logger
        self.name: str = "devplugins"
        self.description: str = "Shows you plugins that you can make by /makeplugin command"

    def getAllFolders(self) -> None:
        for dirs in os.listdir(self.plugin_folder_path):
            if os.path.isdir(os.path.join(self.plugin_folder_path, dirs)):
                plugin_info: dict = json.load(
                    open(os.path.join(dirs, "info.json"), 'r'))
                name = plugin_info["name"]