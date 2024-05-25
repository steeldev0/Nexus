import nextcord
from nextcord.ext import commands, tasks
import sqlite3
from datetime import datetime, timedelta
import os, os.path
import asyncio
import re
from urllib.parse import urlparse
import threading
import platform
from dotenv import load_dotenv
from pathlib import Path
import glob
import cv2
from PIL import Image

startTime = datetime.now()
intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True
load_dotenv()

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
    global admin_ids, owner_ids, admin_emoji, owner_emoji
    while True:
        with open("admins.txt", "r", encoding="utf-8") as file:
            admin_ids = [int(line.strip()) for line in file]

        with open("settings.txt", "r", encoding="utf-8") as file:
            settings = {line.split('=')[0].strip(): line.split('=')[1].strip() for line in file}
            admin_emoji = settings.get('admin_emoji', '🛡️')
            owner_emoji = settings.get('owner_emoji', '👑')

        with open("owners.txt", "r", encoding="utf-8") as file:
            owner_ids = [int(line.strip()) for line in file]
        
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

@bot.event
async def on_message(message):
    if message.author.bot or message.content.startswith('/'):
        return

    c.execute("SELECT channel_id FROM channel_settings WHERE server_id = ?", (message.guild.id,))
    set_channel_id = c.fetchone()
    if set_channel_id and message.channel.id == set_channel_id[0]:
        with open("banned_users.txt", "r") as banned_file:
            banned_users = banned_file.readlines()
            banned_users = [user.strip() for user in banned_users]

        if str(message.author.id) in banned_users:
            embed = nextcord.Embed(
                title="You are banned from using Nexus",
                description="Please contact an administrator for more information.",
                color=nextcord.Color.red()
            )
            try:
                await message.author.send(embed=embed)
            except nextcord.Forbidden:
                pass
            await message.delete()
            return

        links = re.findall(r'https?://\S+', message.content)
        if links:
            unblocked_domains = []
            with open("unblocked_links.txt", "r", encoding="utf-8") as file:
                for line in file:
                    unblocked_domains.append(urlparse(line.strip()).netloc)
            
            allow_message = False
            for link in links:
                domain = urlparse(link).netloc
                if domain in unblocked_domains:
                    allow_message = True
                    break
            
            if not allow_message:
                embed = nextcord.Embed(
                    title="Alert!",
                    description="You cannot send links on Nexus for obvious reasons.",
                    color=nextcord.Color.red()
                )
                try:
                    await message.author.send(embed=embed)
                except nextcord.Forbidden:
                    pass
                await message.delete()
                return

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
            embed.set_author(name=f"{message.author.display_name} | {message.author.id} | {admin_emoji if message.author.id in admin_ids else ''} {owner_emoji if message.author.id in owner_ids else ''}", icon_url=icon_url)
        else:
            embed.set_author(name=f"{message.author.display_name} | {message.author.id} | {admin_emoji if message.author.id in admin_ids else ''} {owner_emoji if message.author.id in owner_ids else ''}")

        if message.attachments:
            for attachment in message.attachments:
                await attachment.save("image") 
                video_capture = cv2.VideoCapture("image")
                still_reading, image = video_capture.read()
                frame_count = 0
                while still_reading:
                    cv2.imwrite(f"tempframes/frame_{frame_count:03d}.jpg", image)
                    still_reading, image = video_capture.read()
                    frame_count += 1
                listfiles = next(os.walk("tempframes"))[2]
                files = len(listfiles)
                print(files)
                if files > 150:
                    print ("Too much frames.")
                    files = os.listdir("tempframes")
                    for file in files:
                        file_path = os.path.join("tempframes", file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    print("Temporary frames cleaned.")
                    return
                else: 
                    images = glob.glob(f"tempframes/*.jpg")
                    images.sort()
                    frames = [Image.open(image) for image in images]
                    frame_one = frames[0]
                    frame_one.save("output.gif", format="GIF", append_images=frames, save_all=True, fps=5, loop=0, quality=50, optimize=True)
                    files = os.listdir("tempframes")
                    for file in files:
                        file_path = os.path.join("tempframes", file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    print("Temporary frames cleaned.")
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
                tasks.append(send_message(channel, embed))

        await asyncio.gather(*tasks)
xy_file = Path('output.gif')
async def send_message(channel, embed):
    try:
        if xy_file.is_file():
          try:
             file = nextcord.File("output.gif", filename='attch.gif')
             embed.set_image(url="attachment://attch.gif")
             await channel.send(embed=embed, file=file)
             os.remove("output.gif")
             os.remove("image")
          except:
             # Uncommented due to spamming
             # await channel.send("An error occured while sending your image. Please try again.")
             # await channel.send("NOTE: Usually this happens when your file has too much frames, or when you use a unsupported file format!")
             return
        else:
          await channel.send(embed=embed)
    except nextcord.Forbidden:
        pass
        

async def delete_message(message):
    try:
        await asyncio.sleep(0.89)
        await message.delete()
    except nextcord.Forbidden:
        pass

def load_commands(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.py'):
            with open(os.path.join(directory, filename), 'r', encoding="utf-8") as file:
                exec(file.read())

load_commands("src/commands")
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(DISCORD_TOKEN)

