@bot.slash_command(description="Informations about the bot")
async def about(ctx):
    embed = nextcord.Embed(
            title="About this bot:",
            description=" ",
            color=nextcord.Color.blue()
    )
    embed.insert_field_at(0, name = f"""Operating System""", value=platform.platform(), inline=False)
    embed.insert_field_at(1, name = f"""Bot's uptime(HH:MM:SS.MS)""", value=datetime.now() - startTime, inline=False)
    await ctx.send(embed=embed)
