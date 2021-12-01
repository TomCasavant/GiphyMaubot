from typing import Type
import urllib.parse
import random
from mautrix.types import RoomID, ImageInfo
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from maubot import Plugin, MessageEvent
from maubot.handlers import command


# Setup config file
class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("giphy_api_key")
        helper.copy("tenor_api_key")
        helper.copy("provider")
        helper.copy("source")
        helper.copy("response_type")
        helper.copy("num_results")
        helper.copy("rating")


class GiphyPlugin(Plugin):
    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()

    async def send_gif(
        self, room_id: RoomID, gif_link: str, query: str, info: dict
    ) -> None:
        resp = await self.http.get(gif_link)
        if resp.status != 200:
            self.log.warning(f"Unexpected status fetching image {url}: {resp.status}")
            return None

        data = await resp.read()
        mime = info["mime"]
        filename = f"{query}.gif" if len(query) > 0 else "giphy.gif"
        uri = await self.client.upload_media(data, mime_type=mime, filename=filename)

        await self.client.send_image(
            room_id,
            url=uri,
            file_name=filename,
            info=ImageInfo(
                mimetype=info["mime"], width=info["width"], height=info["height"]
            ),
        )

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    @command.new(
        "giphy",
        aliases=("gif", "g", "tenor"),
    )
    @command.argument("search_term", pass_raw=True, required=False)
    async def handler(self, evt: MessageEvent, search_term: str) -> None:
        await evt.mark_read()
        if not search_term:
            # If user doesn't supply a search term, set to empty string
            search_term = ""
            source = self.config["source"]
        else:
            source = "translate"

        if self.config["provider"] == "giphy":
            api_key = self.config["giphy_api_key"]
            url_params = urllib.parse.urlencode({"s": search_term, "api_key": api_key, "rating": rating})
            response_type = self.config["response_type"]
            # Get random gif url using search term
            async with self.http.get(
                "http://api.giphy.com/v1/gifs/{}?{}".format(source, url_params)
            ) as response:
                data = await response.json()

            # Retrieve gif link from JSON response
            try:
                gif_link = data["data"]["images"]["original"]["url"]
                info = {}
                info["width"] = data["data"]["images"]["original"]["width"]
                info["height"] = data["data"]["images"]["original"]["height"]
                info["mime"] = "image/gif"  # this shouldn't really change
            except Exception as e:
                await evt.respond("Blip bloop... Something is wrecked up here!")
                return None

        elif self.config["provider"] == "tenor":
            api_key = self.config["tenor_api_key"]
            url_params = urllib.parse.urlencode({"q": search_term, "key": api_key})
            response_type = self.config["response_type"]
            # Get random gif url using search term
            async with self.http.get(
                "https://g.tenor.com/v1/search?{}".format(url_params)
            ) as response:
                data = await response.json()

            # Retrieve gif link from JSON response
            try:
                image_num = random.randint(0, self.config["num_results"] - 1)
                gif_link = data["results"][image_num]["media"][0]["gif"]["url"]
                info = {}
                info["width"] = data["results"][image_num]["media"][0]["gif"]["dims"][0]
                info["height"] = data["results"][image_num]["media"][0]["gif"]["dims"][
                    1
                ]
                info["mime"] = "image/gif"  # this shouldn't really change
            except Exception as e:
                await evt.respond("Blip bloop... Something is wrecked up here!")
                return None
        else:
            raise (Exception("Wrong provider:", self.config["provider"]))

        if response_type == "message":
            await evt.respond(gif_link, allow_html=True)  # Respond to user
        elif response_type == "reply":
            await evt.reply(gif_link, allow_html=True)  # Reply to user
        elif response_type == "upload":
            await self.send_gif(
                evt.room_id, gif_link, search_term, info
            )  # Upload the GIF to the room
        else:
            await evt.respond(
                "something is wrong with my config, be sure to set a response_type"
            )
