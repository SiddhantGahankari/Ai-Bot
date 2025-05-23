import discord
import aiohttp
import asyncio
import os
import webserver  # Assumes this defines keep_alive()

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

    content = message.content.strip()

    # Ignore legacy '!' commands
    if content.startswith('!'):
        return

    # Help command
    if content.lower().startswith('#help'):
        help_text = (
            "**🤖 Deepseek Bot Help:**\n"
            "Use `#ask <your question>` to get a response from the Deepseek model.\n"
            "Example: `#ask What's the future of AI?`\n\n"
            "`#help` - Show this help message"
        )
        await message.channel.send(help_text)
        return

    # Ask command
    if content.startswith('#ask'):
        query = content[len('#ask '):].strip()
        if not query:
            await message.channel.send("Please provide something to deepseek!")
            return

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

                            # Split response into chunks of 1990 characters
                            chunks = [reply[i:i+1990] for i in range(0, len(reply), 1990)]
                            for i, chunk in enumerate(chunks):
                                prefix = "" if i == 0 else "*continued...*\n"
                                await message.channel.send(f"```markdown\n{prefix}{chunk}\n```")
                        else:
                            try:
                                error_info = await response.json()
                            except Exception:
                                error_info = await response.text()
                            await message.channel.send(f"API call failed with status {response.status}:\n```{error_info}```")
                except Exception as e:
                    await message.channel.send(f"Something went wrong: `{str(e)}`")

# Keep server alive (if hosted on Replit or similar)
webserver.keep_alive()
client.run(DISCORD_TOKEN)
