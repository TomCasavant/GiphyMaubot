from typing import Type
from mautrix.types import EventType
from maubot import Plugin, MessageEvent
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from maubot.handlers import command
import requests


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
    @command.argument("searchTerm", pass_raw=True, required=False)
    async def handler(self, evt: MessageEvent, searchTerm: str) -> None:
        await evt.mark_read()
        if not searchTerm:
            #If user doesn't supply a search term, set to empty string
            searchTerm = ""
        api_key = self.config["api_key"]
        #Get random gif url using search term
        data = requests.get("http://api.giphy.com/v1/gifs/random?tag={}&api_key={}".format(searchTerm, api_key)).json()
        gifLink = data['data']['image_url']

        await evt.reply(gifLink, html_in_markdown=True) #Reply to user

