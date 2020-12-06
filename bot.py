import discord
import os
import thresholding
import tempfile
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PREFIX = os.getenv("PREFIX")

client = discord.Client()


@client.event
async def on_ready():
    print("Logged in as: {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith(PREFIX):
        return

    if message.content.endswith("help"):
        await message.channel.send(
            "```\nOnly one command: baboon! [window] [offset]\n"
            + "Typing baboon! will have me perform and adaptive Mean-C threshold on the last sent image\n"
            + "Extra parameters are windowsize and offset, and are specified by entering 2 integers separated by spaces```"
        )
        return

    # Bot called, attempt to read for last image sent
    # TODO Return to change the limit variable below later on, based on experience

    image = None
    window = 5
    offset = 10

    async for past_message in message.channel.history(limit=15):
        if len(past_message.attachments) == 1:
            image = past_message.attachments[0]
            split_message = message.content.split(" ")
            if (len(split_message)) > 1:
                window = int(split_message[1])
                print(window)
            if (len(split_message)) > 2:
                offset = int(split_message[2])
                print(offset)
            break

    if image is None:
        print("No dice")
        await message.channel.send("No image found")
        return

    with tempfile.TemporaryDirectory() as tmpdirname:
        await image.save(f"{tmpdirname}/{image.filename}")
        output_file = thresholding.adaptive_mean_C(
            f"{tmpdirname}/{image.filename}", window, offset
        )
        await message.channel.send("Cripsy!", file=discord.File(output_file))


client.run(BOT_TOKEN)
