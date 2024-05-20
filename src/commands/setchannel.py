@bot.slash_command(description="Sets the channel to start cross-guild chatting :)")
async def setchannel(ctx):
    if ctx.user.guild_permissions.manage_guild:
        c.execute("SELECT channel_id FROM channel_settings WHERE server_id = ?", (ctx.guild.id,))
        result = c.fetchone()
        if result:
            await ctx.send("Your server already has a channel set for cross-guild chatting.")
        else:
            c.execute("INSERT OR REPLACE INTO channel_settings (server_id, channel_id) VALUES (?, ?)",
                      (ctx.guild.id, ctx.channel.id))
            conn.commit()
            await ctx.send("Channel set successfully!")
    else:
        await ctx.send("You need to have the 'manage server' permission to use this command.")