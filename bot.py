import discord
import aiohttp
import asyncio
import os
improt webserver
DISCORD_TOKEN = os.environ['discordkey']
OPENROUTER_API_KEY = os.environ['apikey']

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot is online as {client.user}!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!ask'):
        query = message.content[len('!ask '):].strip()
        if not query:
            await message.channel.send("Please provide something to deepseek!")
            return

        # Typing indicator
        async with message.channel.typing():
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        'https://openrouter.ai/api/v1/chat/completions',
                        headers={
                            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                            'Content-Type': 'application/json'
                        },
                        json={
                            "model": "deepseek/deepseek-chat",
                            "messages": [{"role": "user", "content": query}],
                            "temperature": 0.7
                        }
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            reply = data['choices'][0]['message']['content']
                            await message.channel.send(f"```markdown\n{reply}\n```")
                        else:
                            try:
                                error_info = await response.json()
                            except Exception:
                                error_info = await response.text()
                            await message.channel.send(f"API call failed with status {response.status}:\n{error_info}")
                except Exception as e:
                    await message.channel.send(f"Something went wrong: {str(e)}")

webserver.keep_alive()
client.run(DISCORD_TOKEN)
