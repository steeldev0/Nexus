@bot.slash_command(description="OWNER-ONLY: Unset channel to log incoming reports.")
async def unsetreportlogchannel(ctx):
    if ctx.user.guild_permissions.manage_guild and ctx.user.id in owner_ids:
        c.execute(
            "SELECT * FROM reportlogs_settings WHERE server_id = ?",
            (ctx.guild.id,),
        )
        result = c.fetchone()
        if not result:
            await ctx.send("Channel not set, yet.")
        else:
            c.execute("DELETE FROM reportlogs_settings WHERE server_id = ?", (ctx.guild.id,))
            c.execute("DELETE FROM reportlogs_settings WHERE channel_id = ?", (ctx.channel.id,))
            conn.commit()
            await ctx.send("Channel unset successfully.")
    else:
        await ctx.send(
            "Whoops! Make sure you are the bot-owner, and you have the 'manage server' permission."
        )
# Hi from user0!
