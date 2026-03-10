# !pip install llama-cpp-python

import os
from datetime import timedelta
from llama_cpp import Llama

import discord
import dotenv
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

dotenv.load_dotenv()
with open("config.toml", "rb") as f:
    config = tomllib.load(f)

CYAN = "\033[36m"
GREY = "\033[90m"
DEFAULT = "\033[m"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


async def direct_msg(message, author_message):
    user = await client.fetch_user(author_message.author.id)
    if user.dm_channel is None:
        await user.create_dm()
    try:
        await user.dm_channel.send(message)
    except (discord.Forbidden, discord.HTTPException):
        print(f"Couldn't DM {author_message.author.name}.")


def get_channel(message):
    if message.guild is None:
        return f"Direct Message"
    else:
        return str(message.channel)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}\n")


@client.event
async def on_message(message):
    print(
        GREY
        + f"[{get_channel(message)}] "
        + CYAN
        + f"{message.author.name}: "
        + DEFAULT
        + message.content
    )

    if message.guild is None:
        return

    if (
        message.author == client.user or message.author.guild_permissions.administrator
    ) and not config["debug"]["debug_mode"]:
        return

    for item in config["moderation"]["delete"]:
        if item.lower() in message.content.lower():
            await message.delete()
            await direct_msg(
                f"Your message has been deleted because your message contains banned text: {item}",
                message,
            )

    for item in config["moderation"]["kick"]:
        if item.lower() in message.content.lower():
            await message.delete()

            member = message.guild.get_member(message.author.id)
            if member is None:
                try:
                    member = await message.guild.fetch_member(message.author.id)
                except discord.NotFound:
                    print(f"Could not fetch member {message.author.name}.")
                    continue

            await direct_msg(
                f"Your account has been kicked because your message contains banned text: {item}",
                message,
            )

            try:
                await member.kick(reason="Sending banned text")
            except discord.Forbidden:
                print(f"Insufficient permissions to kick {message.author.name}.")
                continue

            continue

    for item in config["moderation"]["ban"]:
        if item.lower() in message.content.lower():
            await message.delete()

            member = message.guild.get_member(message.author.id)
            if member is None:
                try:
                    member = await message.guild.fetch_member(message.author.id)
                except discord.NotFound:
                    print(f"Could not fetch member {message.author.name}.")
                    continue

            try:
                try:
                    await member.ban(reason=f"Sending banned text")
                except discord.Forbidden:
                    print(f"Insufficient permissions to ban {message.author.name}.")
                    continue
                await direct_msg(
                    f"Your account has been banned because your message contains banned text: {item}",
                    message,
                )
            except (discord.Forbidden, discord.HTTPException):
                print(f"Couldn't DM {message.author.name}")
            continue

    for item in config["moderation"]["mute"]:
        if item.lower() in message.content.lower():
            await message.delete()

            member = message.guild.get_member(message.author.id)
            if member is None:
                try:
                    member = await message.guild.fetch_member(message.author.id)
                except discord.NotFound:
                    print(f"Could not fetch member {message.author.name}.")
                    continue

            try:
                await member.timeout(
                    timedelta(minutes=config["moderation"]["time_to_mute"]),
                    reason="Sending banned text",
                )
            except discord.Forbidden:
                print(f"Insufficient permissions to mute {message.author.name}.")
                continue

            await direct_msg(
                f"Your account has been muted for {config['moderation']['time_to_mute']} because your message contains banned text: {item}",
                message,
            )
            continue

    if len(message.content) >= config["ai"]["min_chars"]:
        response = llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": config["ai"]["system_prompt"]},
                {
                    "role": "user",
                    "content": config["ai"]["user_prompt"].replace(
                        "{{INPUT}}", message.content
                    ),
                },
            ]
        )
        output = response["choices"][0]["message"]["content"]
        if "<scam>" in output.strip().lower():
            await message.delete()
            print(f"AI response: {output}")
        elif "<fine>" in output.strip().lower():
            print(f"AI response: {output}")
        else:
            print(f"Invalid AI response: {output}")


if __name__ == "__main__":
    model_path = config["ai"]["model_path"]
    if not model_path:
        raise ValueError(
            "model_path not set in config.toml. Add the path to your GGUF model file."
        )
    llm = Llama(model_path=model_path, chat_format="chatml")

    client.run(os.getenv("BOT_TOKEN"))