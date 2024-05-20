@bot.slash_command(description="Unsets the channel for cross-guild chatting")
async def unset(ctx):
    if ctx.user.guild_permissions.manage_guild:
        c.execute("SELECT channel_id FROM channel_settings WHERE server_id = ?", (ctx.guild.id,))
        result = c.fetchone()
        if not result:
            await ctx.send("This server isnt set yet")
        else:
            c.execute("DELETE FROM channel_settings WHERE server_id = ?", (ctx.guild.id,))
            conn.commit()
            await ctx.send("Channel unset successfully")
    else:
        await ctx.send("You need to have the manage server permission to use this command")