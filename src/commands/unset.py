from db import *

@bot.slash_command(description="Unsets the channel for cross-guild chatting")
async def unset(ctx):
    if ctx.user.guild_permissions.manage_guild:
        result = Channel.select(Channel.channel_id).where(Channel.server_id == ctx.guild.id)
        if not result:
            await ctx.send("This server isnt set yet")
        else:
            Channel.delete().where(Channel.server_id == ctx.guild.id).execute()
            await ctx.send("Channel unset successfully")
    else:
        await ctx.send("You need to have the manage server permission to use this command")