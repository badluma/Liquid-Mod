import os
from datetime import timedelta
import ollama

import discord
import dotenv
import tomllib

dotenv.load_dotenv()
with open("config.toml", "rb") as f:
    config = tomllib.load(f)

intents = discord.Intents.default()
intents.message_content = True

messages_to_review = []

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
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
        messages_to_review.append(message)

if __name__ == '__main__':
    model_name = config["ai"]["model"]
    while messages_to_review:
        current_message = messages_to_review.pop(0)
        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": config["ai"]["prompt"].replace("%m", current_message.content)}]
        )
        output = response["message"]["content"]
        if "<scam>" in output.strip().lower():
            current_message.delete()
        elif "<fine>" in output.strip.lower():
            pass
        else:
            print(f"Invalid AI response: {output}")

    client.run(os.getenv('BOT_TOKEN'))