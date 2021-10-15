# Giphy Maubot
A simple [maubot](https://github.com/maubot/maubot) that generates a random gif given a search term.

## Setup
1. Get API key from [giphy](https://developers.giphy.com/docs/) and [tenor](https://tenor.com/gifapi)
2. Fill in `giphy_api_key` and `tenor_api_key` field in base-config.yaml config file or in online maubot config editor
3. Decide what (giphy) endpoint to get random gifs from (e.g. trending, random) in config file
4. Choose a response type:
  - `message` will send a regular message to the room
  - `reply` will send a quoted reply message to the room
  - `upload` will actually upload the GIF as an image to the room


## Usage
`!gif word` - Bot replies with a link to a gif given the search term
`!gif` - Bot replies with a link to a random gif

Also, `!giphy`, `!g` and `!tenor` may be used.
