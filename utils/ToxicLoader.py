from shutil import Error
from typing import TYPE_CHECKING
from time import sleep

import os
import json

if TYPE_CHECKING:
    from podrum.version import version
    from podrum.server import server


class ToxicLoader:

    """
        ...

        Attributes
        ----------
        input_folder : str
            Path to the folder with the plugins to load.
        output_folder : str
            Path to the folder where the loaded plugins will be stored.
        check_if_wants : bool
            If True, the loaded plugins will be checked if they want to be loaded by DevTools.
        server : 'server'
            The server instance.

    """

    def __init__(self, input_folder: str, output_folder: str, check_if_wants: bool, server: 'server') -> None:
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.check_if_wants = check_if_wants
        self.server = server
        self.logger = server.logger
        sleep(10)

    def validate_plugin_json(self, plugin_json: dict) -> list[bool, str]:
        """
            Validates the plugin json.

            Parameters
            ----------
            plugin_json : dict
                The plugin json.

            Returns
            -------
            list[bool, str]
                [True, ""]
                    if the plugin json is valid.
                [False, error_message: str]
                    if the plugin json is not valid.
        """
        errors: list[str] = []
        if not "name" in plugin_json:
            errors.append("Missing plugin name")
        if not "version" in plugin_json:
            errors.append("Missing plugin version")
        if not "api_version" in plugin_json:
            errors.append("Missing plugin api_version")
        if plugin_json["api_version"] != version.podrum_api_version:
            errors.append(
                f"Plugin api_version is not the same as the server api_version!\nPlugin api_version: {plugin_json['api_version']}\nServer api_version: {version.podrum_api_version}"
                )
        if not "main" in plugin_json:
            errors.append("Missing plugin main class")

        if len(errors) > 0:
            return [False, "\n".join(errors)]
        return [True, ""]

    def load_plugin(self, plugin_path: str) -> None:
        """
            Loads a plugin by its path.

            Parameters
            ----------
            plugin_path : str
                Path to the plugin to load.
        """
        if not os.path.exists(os.path.join(plugin_path, "info.json")):
            FileNotFoundError(
                f"{plugin_path}/info.json not found!\nNOT VALID PLUGIN STRUCTURE!!!")
            return  # ? xD

        plugin_info: dict = json.load(
            open(os.path.join(plugin_path, "info.json"), 'r')
        )

        if(not self.validate_plugin_json(plugin_info)[0]):
            Error(
                f"{plugin_path}/info.json is not valid!\n{self.validate_plugin_json(plugin_info)[1]}")

        name = plugin_info["name"]
        if name in self.server.plugin_manager.plugins:
            self.server.logger.info(f"Already loaded {name}")
            return
        main = plugin_info["main"]
        plugin_version = plugin_info["version"]
