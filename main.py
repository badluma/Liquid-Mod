import os
from datetime import timedelta
import ollama

import discord
import dotenv
import tomllib

dotenv.load_dotenv()
with open("config.toml", "rb") as f:
    config = tomllib.load(f)

CYAN = '\033[36m'
GREY = '\033[90m'
DEFAULT = '\033[m'

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}\n')


@client.event
async def on_message(message):
    print(GREY + f"[{message.channel}] " + CYAN + f"{message.author.name}:" + DEFAULT)
    print(message.content)
    print()

    if (message.author == client.user or message.author.guild_permissions.administrator) and not config["debug"]["debug_mode"]:
        return

    for item in config["moderation"]["delete"]:

        if item.lower() in message.content.lower():

            await message.delete()

            try:
                await message.author.send(f"Your message has been deleted because it contains banned text: {item}")
            except discord.Forbidden:
                print(f"Couldn't DM {message.author.name}.")
            continue


    for item in config["moderation"]["kick"]:

        if item.lower() in message.content.lower():

            await message.delete()

            try:
                await message.author.kick(reason="Sending banned text")
            except discord.Forbidden:
                print(f"Insufficient permissions to kick {message.author.name}.")
                continue

            try:
                await message.author.send(f"Your account has been kicked because your message contains banned text: {item}")
            except discord.Forbidden:
                print(f"Couldn't DM {message.author.name}.")
            continue


    for item in config["moderation"]["ban"]:

        if item.lower() in message.content.lower():

            await message.delete()

            try:
                await message.author.ban(reason=f"Sending banned text")
            except discord.Forbidden:
                print(f"Insufficient permissions to ban {message.author.name}.")
                continue

            try:
                await message.author.send(f"Your account has been banned because your message contains banned text: {item}")
            except discord.Forbidden:
                print(f"Couldn't DM {message.author.name}")
            continue


    for item in config["moderation"]["mute"]:

        if item.lower() in message.content.lower():

            await message.delete()

            try:
                await message.author.timeout(timedelta(minutes=config["moderation"]["time_to_mute"]), reason="Sending banned text")
            except discord.Forbidden:
                print(f"Insufficient permissions to mute {message.author.name}.")
                continue

            try:
                await message.author.send(f"Your account has been timed out for {config['moderation']['time_to_mute']} minutes because your message contains banned text: {item}")
            except discord.Forbidden:
                print(f"Couldn't DM {message.author.name}.")
            continue

    if len(message.content) >= config["ai"]["min_chars"]:
        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": config["ai"]["system_prompt"]},
                {"role": "user", "content": config["ai"]["user_prompt"].replace("{{INPUT}}", message.content)}
            ]
        )
        output = response["message"]["content"]
        if "<scam>" in output.strip().lower():
            await message.delete()
            print(f"AI response: {output}")
        elif "<fine>" in output.strip().lower():
            print(f"AI response: {output}")
        else:
            print(f"Invalid AI response: {output}")

if __name__ == '__main__':
    model_name = config["ai"]["model"]

    client.run(os.getenv('BOT_TOKEN'))