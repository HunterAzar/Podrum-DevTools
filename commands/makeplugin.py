from podrum.console.logger import logger
from podrum.protocol.mcbe.mcbe_player import mcbe_player
import shutil as zip


class make_plugin:
    def __init__(self, server: object) -> None:
        self.server: object = server
        self.logger: logger = self.server.logger
        self.name: str = "makeplugin"
        self.description: str = "Makes ZIP file from your plugin and copies to plugin folder"

    def execute(self, args: list, sender: mcbe_player) -> None:
        if len(args) <= 0:
            sender.send_message(
                "Usage: \nmakeplugin <plugin name>\nFor checking which plugin you can make type '/devplugins'")
            return
        manager = self.server.managers.plugin_manager
        if args[0] in manager.plugins:
            plugin = manager.plugins[args[0]]
            self.logger.success(f"{args[0]} found!!!")
            if hasattr(plugin, "devtools"):
                if plugin.devtools == "true" and plugin.allow_dev == "true" if hasattr(plugin, "allow_dev") else plugin.allow_dev == "true":
                    self.logger.info("Making new ZIP file")
                    zip.make_archive(f"{plugin.name}", "zip", f"{plugin.path}")
                    zip.move(f"{plugin.name}.zip",
                             f"{plugin.path}\\..\\{plugin.name}.zip")
                    self.logger.success(
                        f"Successfully maked plugin Archive for {plugin.name}")
                else:
                    self.logger.warn(
                        f"{plugin.name} doesn't want to be edited -> {plugin.__name__}.allow_dev == false")
            else:
                self.logger.warn(f"Plugin is not loaded by DevTools plugin")
