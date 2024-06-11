import nextcord
from nextcord.ext import commands, tasks
import sqlite3
from datetime import datetime, timedelta
import os
import asyncio
import re
from urllib.parse import urlparse
import threading
from wcmatch import glob
from flask import Flask, jsonify, request
import platform

naviac = 975365560298795008
last_message = None

startTime = datetime.now()
intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

statuses = ["Connecting servers", "Chatting with other servers", "Making servers popular"]

async def update_status():
    for status in statuses:
        await bot.change_presence(activity=nextcord.Game(name=status))
        await asyncio.sleep(5)

conn = sqlite3.connect('nexus.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS channel_settings
             (server_id INTEGER, channel_id INTEGER, PRIMARY KEY (server_id, channel_id))''')
conn.commit()

async def reload_roles():
    global admin_ids, owner_ids, manager_ids, admin_emoji, owner_emoji, manager_emoji
    while True:
        with open("admins.txt", "r", encoding="utf-8") as file:
            admin_ids = [int(line.strip()) for line in file]

        with open("settings.txt", "r", encoding="utf-8") as file:
            settings = {line.split('=')[0].strip(): line.split('=')[1].strip() for line in file}
            admin_emoji = settings.get('admin_emoji', '🛡️')
            owner_emoji = settings.get('owner_emoji', '👑')
            manager_emoji = settings.get('manager_emoji', '🛠️')

        with open("owners.txt", "r", encoding="utf-8") as file:
            owner_ids = [int(line.strip()) for line in file]

        with open("managers.txt", "r", encoding="utf-8") as file:
            manager_ids = [int(line.strip()) for line in file]
        
        await asyncio.sleep(5)

bot.loop.create_task(reload_roles())

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    update_status_loop.start()

update_status_loop = tasks.loop(seconds=5)(update_status)

def format_timestamp(timestamp):
    now = datetime.utcnow()
    message_time = datetime.utcfromtimestamp(timestamp)
    if message_time.date() == now.date():
        return f"Today at {message_time.strftime('%I:%M %p')}"
    elif message_time.date() == now.date() - timedelta(days=1):
        return f"Yesterday at {message_time.strftime('%I:%M %p')}"
    else:
        return message_time.strftime('%Y-%m-%d at %I:%M %p')

async def is_user_banned(user_id):
    try:
        with open('banned_users.txt', 'r') as file:
            banned_users = [int(line.strip()) for line in file]
            return user_id in banned_users
    except FileNotFoundError:
        return False

async def send_ban_notification(user):
    embed = nextcord.Embed(
        title="Nexus Moderation",
        description="You are banned from using Nexus. If you think this is a mistake, contact @steeldev",
        color=nextcord.Color.red()
    )
    try:
        await user.send(embed=embed)
    except nextcord.Forbidden:
        pass

@bot.event
async def on_message(message):
    global last_message
    if (message.author.bot and message.author.id != naviac) or message.content.startswith('/'):
        return
    
    if await is_user_banned(message.author.id):
        await send_ban_notification(message.author)

        # Check if the message is in a set channel
        c.execute("SELECT channel_id FROM channel_settings WHERE server_id = ? AND channel_id = ?", (message.guild.id, message.channel.id))
        if c.fetchone():
            await delete_message(message)
        return

    c.execute("SELECT channel_id FROM channel_settings WHERE server_id = ?", (message.guild.id,))
    set_channel_id = c.fetchone()
    if set_channel_id and message.channel.id == set_channel_id[0]:
        last_message = {
            "username": message.author.name,
            "content": message.content,
            "server": message.guild.name
        }
        await asyncio.gather(
            send_embed(message),
            delete_message(message)
        )

async def send_embed(message):
    server = bot.get_guild(message.guild.id)
    if server:
        if message.guild.id == 1228831727749697648:
            embed_color = nextcord.Color.greyple()
        else:
            embed_color = nextcord.Color.blue()
            
        embed = nextcord.Embed(
            description=f"{message.content}",
            color=embed_color
        )
        icon_url = message.author.avatar.url if message.author.avatar else None
        if icon_url:
            embed.set_author(name=f"{message.author.display_name} | {message.author.id} | "
                      f"{admin_emoji if message.author.id in admin_ids else ''} "
                      f"{owner_emoji if message.author.id in owner_ids else ''} "
                      f"{manager_emoji if message.author.id in manager_ids else ''}",
                 icon_url=icon_url)
        else:
            embed.set_author(name=f"{message.author.display_name} | {message.author.id} | "
                      f"{admin_emoji if message.author.id in admin_ids else ''} "
                      f"{owner_emoji if message.author.id in owner_ids else ''} "
                      f"{manager_emoji if message.author.id in manager_ids else ''}",
                 icon_url=icon_url)

        if message.attachments:
            for attachment in message.attachments:
                await attachment.save(attachment.filename)
            for file in glob.glob('*.{mp4,avi}', flags=glob.BRACE):
                embed.add_field(name=":arrow_up: VIDEO :arrow_up:", value="The author of this message sent the video above.", inline=False)
        if message.author.id in admin_ids or message.author.id in owner_ids:
            embed.color = nextcord.Color.red()

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1090262735478071360/1238197066271031376/NexusChat.png?ex=663e6861&is=663d16e1&hm=9715dd1020c504b6f14bb8b1de8b8c60b0376caadd4ace3b2bc71662b748749f&")
        
        icon_url_guild = message.guild.icon.url if message.guild.icon else None
        if icon_url_guild:
            embed.set_footer(text=f"{server.name} - Nexus Solar - {format_timestamp(message.created_at.timestamp())}", icon_url=icon_url_guild)
        else:
            embed.set_footer(text=f"{server.name} - Nexus Solar - {format_timestamp(message.created_at.timestamp())}")
            
        if message.reference and message.reference.message_id:
            referenced_message = await message.channel.fetch_message(message.reference.message_id)
            if referenced_message and referenced_message.author.bot:
                referenced_description = referenced_message.embeds[0].description
                original_sender = referenced_message.embeds[0].author.name.split(' | ')[0]
                embed.title = f"RE: {original_sender}"
                embed.insert_field_at(0, name="Original Message", value=referenced_description, inline=False)
                embed.description = message.content

        c.execute("SELECT channel_id FROM channel_settings")
        results = c.fetchall()
        tasks = []
        for result in results:
            channel_id = result[0]
            channel = bot.get_channel(channel_id)
            if channel:
                tasks.append(send_message(channel, embed, message.author.id))

        await asyncio.gather(*tasks)

async def send_message(channel, embed, author_id):
    try:
        for file in glob.glob('*.{jpg,png,bmp,webp,jpeg}', flags=glob.BRACE):
            file_dsc = nextcord.File(file, filename="media.jpg")
            embed.set_image(url="attachment://media.jpg")
        for file in glob.glob('*.gif', flags=glob.BRACE):
            file_dsc = nextcord.File(file, filename="media.gif")
            embed.set_image(url="attachment://media.gif")
        for file in glob.glob('*.{mp4,avi}', flags=glob.BRACE):
            file_dsc = nextcord.File(file, filename="media.mp4")
            embed.video.url = "attachment://media.mp4"
        glob_search = glob.glob('*.{mp4,avi,jpg,png,webp,jpeg,avi,gif}', flags=glob.BRACE)
        if not glob_search:
            await channel.send(embed=embed)
        else:
            await channel.send(embed=embed, file=file_dsc)
            for file in glob.glob('*.{mp4,avi,jpg,png,webp,jpeg,avi,gif}', flags=glob.BRACE):
                os.remove(file)
    except nextcord.Forbidden:
        pass
    except Exception as e:
        with open('banned_users.txt', 'a') as f:
            f.write(f"{author_id}\n")

async def delete_message(message):
    try:
        await message.delete()
    except nextcord.Forbidden:
        pass
    
def load_commands(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.py'):
            with open(os.path.join(directory, filename), 'r', encoding="utf-8") as file:
                exec(file.read())
                
@bot.command()
async def ping(ctx):
    await ctx.send("pong!")

load_commands("src/commands")

app = Flask(__name__)

@app.route('/getmessage', methods=['POST', 'GET'])
def get_last_message():
    global last_message
    if request.method == 'POST':
        return jsonify(last_message)
    elif request.method == 'GET':
        if last_message:
            return jsonify(last_message)
        else:
            return jsonify({"message": "No messages sent yet."})
    
@app.route('/send_message', methods=['POST'])
def handle_send_message():
    username = request.headers.get('username')
    message = request.headers.get('message')
    
    if not username or not message:
        return "Missing 'username' or 'message' in headers", 400
    
    asyncio.run_coroutine_threadsafe(send_global_message(username, message), bot.loop)
    return "Message sent", 200

async def send_global_message(username, message):
    try:
        embed = nextcord.Embed(
            description=message,
            color=nextcord.Color.blue()
        )
        embed.set_author(name=username)
        embed.set_footer(text="Global nexus website")

        c.execute("SELECT channel_id FROM channel_settings")
        results = c.fetchall()
        tasks = []
        for result in results:
            channel_id = result[0]
            channel = bot.get_channel(channel_id)
            if channel:
                tasks.append(send_message(channel, embed))
        
        await asyncio.gather(*tasks)

    except Exception as e:
        print(f"Error sending global message: {e}")

def run_flask():
    app.run(host='0.0.0.0', port=25561)
    
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    with open('token.txt', 'r') as file:
        DISCORD_TOKEN = file.read().strip()
    bot.run(DISCORD_TOKEN)

# hi from steeldev <3
