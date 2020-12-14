import discord
import os
import thresholding
import smoothing
import tempfile
from dotenv import load_dotenv
from PIL import Image

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

    #Find a message with an image, if no image is found it will remain to be none
    async for past_message in message.channel.history(limit=15):
        if len(past_message.attachments) == 1:
            with tempfile.TemporaryDirectory() as tmpdirname:
                filename = past_message.attachments[0].filename
                await past_message.attachments[0].save(f"{tmpdirname}/{filename}")
                image = Image.open(f"{tmpdirname}/{filename}")
            break

    if image is None:
        print("No dice")
        await message.channel.send("No image found")
        return
    print("Found one")
    with tempfile.TemporaryDirectory() as tmpdirname:
        #If an image is found, determine what command was issued
        #Command structure will be [baboon! [Operation name] [Operation type] [param1] [param2] [paramN]]
        split_message = message.content.split(" ")
        for i in range(1, len(split_message)):
            split_message[i] = split_message[i].upper()
        if split_message[1] == "THRESHOLD":
            if split_message[2] == "ADAPTIVE":
                #Only 2 possible parameters for adaptive, window and offset
                #Set defaults
                window = 5
                offset = 10
                if len(split_message) - 1 >= 4:
                    offset = int(split_message[4])
                    window = int(split_message[3])
                elif len(split_message) - 1 == 3:
                    window = int(split_message[3])
                output_file = thresholding.adaptive_mean_C(image, window, offset)
                output_file.save(f"{tmpdirname}/{filename}")
                await message.channel.send("Cripsy!", file=discord.File(f"{tmpdirname}/{filename}"))

            elif split_message[2] == "GLOBAL":
                #Determine whether it will be otsu or manual global by seeing if there is an argument
                if len(split_message) - 1 > 2:
                    #This means a value was passed, so manual thresholding
                    threshold = int(split_message[3])
                else:
                    threshold = None
                output_file = thresholding.global_threshold(threshold, image)
                output_file.save(f"{tmpdirname}/{filename}")
                await message.channel.send("Cripsy!", file=discord.File(f"{tmpdirname}/{filename}"))
        
        if split_message[1] == "SMOOTH":
            if split_message[2] == "MEAN":
                window = 5
                if len(split_message) - 1 >= 3:
                    window = int(split_message[3])
                output_file = smoothing.mean(image, window)
                output_file.save(f"{tmpdirname}/{filename}")
                await message.channel.send("Smoove!", file=discord.File(f"{tmpdirname}/{filename}"))
            elif split_message[2] == "TRIANGLE":
                window = 5
                if len(split_message) - 1 >= 3:
                    window = int(split_message[3])
                output_file = smoothing.triangle(image, window)
                output_file.save(f"{tmpdirname}/{filename}")
                await message.channel.send("Smoove!", file=discord.File(f"{tmpdirname}/{filename}"))
            elif split_message[2] == "GAUSSIAN":
                window = 5
                sigma = 1
                #[baboon!, smooth, gaussian, window, sigma]
                if len(split_message) - 1 >= 4:
                    window = int(split_message[3])
                    sigma = int(split_message[4])
                elif len(split_message) - 1 == 3:
                    window = int(split_message[3])
                output_file = smoothing.gaussian(image, window, sigma)
                output_file.save(f"{tmpdirname}/{filename}")
                await message.channel.send("Smoove!", file=discord.File(f"{tmpdirname}/{filename}"))


client.run(BOT_TOKEN)
