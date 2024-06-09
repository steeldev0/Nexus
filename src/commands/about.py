# watch it bro, u cant change/remove any nexus credits here, u have to give credits for nexus, in any way, u can adjust how credits are given tho

@bot.slash_command(description="Informations about the bot")
async def about(ctx):
    embed = nextcord.Embed(
            title="About this bot:",
            description="""Nexus is your go-to cross guild chatting Discord bot! This bot connects to all your favourite server to form a tree of chatting, enabling you to talk to others and possibly make new frends! There are lots of other servers with this bot; feel free to add it to yours! We hope you enjoy using Nexus! Happy chatting :)
Support server : https://discord.gg/8eF2KhMS5Q""",
            color=nextcord.Color.blue()
    )
    embed.insert_field_at(0, name = f"""Operating System""", value=platform.platform(), inline=False)
    embed.insert_field_at(1, name = f"""Bot's uptime(HH:MM:SS.MS)""", value=datetime.now() - startTime, inline=False)
    await ctx.send(embed=embed)
