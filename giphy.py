from typing import Type
import requests
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from maubot import Plugin, MessageEvent
from maubot.handlers import command


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("api_key")


class GiphyPlugin(Plugin):
    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    @command.new("giphy")
    @command.argument("search_term", pass_raw=True, required=False)
    async def handler(self, evt: MessageEvent, search_term: str) -> None:
        await evt.mark_read()
        if not search_term:
            # If user doesn't supply a search term, set to empty string
            search_term = ""
        api_key = self.config["api_key"]
        # Get random gif url using search term
        async with self.http.get(
            "http://api.giphy.com/v1/gifs/random?tag={}&api_key={}".format(
                search_term, api_key
            )
        ) as response:
            data = await response.json()
        gif_link = data.get("data").get("image_url")

        await evt.reply(gif_link, html_in_markdown=True)  # Reply to user
