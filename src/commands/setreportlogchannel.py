@bot.slash_command(description="OWNER-ONLY: Set channel to log incoming reports.")
async def setreportlogchannel(ctx):
    if ctx.user.guild_permissions.manage_guild and ctx.user.id in owner_ids:
        c.execute(
            "SELECT * FROM reportlogs_settings WHERE server_id = ?",
            (ctx.guild.id,),
        )
        result = c.fetchone()
        if result:
            await ctx.send("Channel already set.")
        else:
            c.execute("INSERT OR REPLACE INTO reportlogs_settings (server_id, channel_id) VALUES (?, ?)",
                      (ctx.guild.id, ctx.channel.id))
            conn.commit()
            await ctx.send("Channel set successfully.")
    else:
        await ctx.send(
            "Whoops! Make sure you are the bot-owner, and you have the 'manage server' permission."
        )
# Hi from user0!
