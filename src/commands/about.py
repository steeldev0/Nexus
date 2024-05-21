@bot.slash_command(description="Informations about the bot")
async def about(ctx):
    embed = nextcord.Embed(
            title="Hello! This bot is based on Nexus.",
            description="Read the text below for more information.",
            color=nextcord.Color.blue()
    )
    embed.insert_field_at(0, name = f"""Sources""", value = "https://github.com/steeldev0/Nexus", inline=False)
    embed.insert_field_at(1, name = f"""Operating System""", value=platform.platform(), inline=False)
    embed.insert_field_at(3, name = f"""Bot's uptime(HH:MM:SS.MS)""", value=datetime.now() - startTime, inline=False)
    await ctx.send(embed=embed)
