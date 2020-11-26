import discord
import os
from ThresholdLib import Thresholding
from dotenv import load_dotenv

load_dotenv()
BotTOKEN = os.getenv("BotTOKEN")
client = discord.Client()

@client.event
async def on_ready():
        print('Logged in as: {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('baboon!'):
        #Bot called, attempt to read for last image sent
        #TODO Return to change the limit variable below later on, based on experience
        image = None
        window = 5
        offset = 10
        async for past_message in message.channel.history(limit = 15):
            if(len(past_message.attachments) == 1):
                image = past_message.attachments[0]
                split_message = message.content.split(" ")
                if(len(split_message)) > 1:
                    window = int(split_message[1])
                    print(window)
                if(len(split_message)) > 2:
                    offset = int(split_message[2])
                    print(offset)
                break
        if image != None:
            print("Found one")
            await image.save(f'./TempImages/{image.filename}')
            #Image saved, now process it
            output_file = Thresholding.adaptive_mean_C('./TempImages/' + image.filename, window, offset)
            await message.channel.send('Cripsy!', file=discord.File(output_file))
            #Now delete the image
            if os.path.exists(output_file):
                os.remove(output_file)
        else:
            print("No dice")
            await message.channel.send('No image found')
    elif message.content.startswith('!belp'):
        await message.channel.send('```\nOnly one command: baboon! [window] [offset]\n' + 
        'Typing baboon! will have me perform and adaptive Mean-C threshold on the last sent image\n' +
        'Extra parameters are windowsize and offset, and are specified by entering 2 integers separated by spaces```')

client.run(BotTOKEN)