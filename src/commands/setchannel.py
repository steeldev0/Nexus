from db import *

@bot.slash_command(description="Sets the channel to start cross-guild chatting :)")
async def setchannel(ctx):
    if ctx.user.guild_permissions.manage_guild:
        result = Channel.select(Channel.channel_id).where(Channel.server_id == ctx.guild.id)
        if result:
            await ctx.send("Your server already has a channel set for cross-guild chatting.")
        else:
            Channel.create(channel_id=ctx.channel.id, server_id=ctx.guild.id)
            await ctx.send("Channel set successfully!")
    else:
        await ctx.send("You need to have the 'manage server' permission to use this command.")