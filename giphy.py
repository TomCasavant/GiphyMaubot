from typing import Type
import urllib.parse
import random
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from maubot import Plugin, MessageEvent
from maubot.handlers import command


# Setup config file
class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("api_key")
        helper.copy("source")


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
            source = self.config["source"]
        else:
            source = "translate"

        api_key = self.config["api_key"]
        url_params = urllib.parse.urlencode({"s": search_term, "api_key": api_key})
        # Get random gif url using search term
        async with self.http.get(
            "http://api.giphy.com/v1/gifs/{}?{}".format(source, url_params)
        ) as response:
            data = await response.json()

        # Retrieve gif link from JSON response
        gif = data.get("data", {})
        gif_exists = True
        if isinstance(gif, list):
            # check if there were no results
            if gif:
                gif_link = random.choice(gif).get("url")
            else:
                gif_exists = False
        else:
            gif_link = gif.get("url")

        if gif_exists:
            await evt.reply(gif_link, html_in_markdown=True)  # Reply to user
