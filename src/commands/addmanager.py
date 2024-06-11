@bot.slash_command(name='addmanager', description='Add a nexus manager')
async def add_manager(ctx: nextcord.Interaction, user: nextcord.User):
    if ctx.user.id not in owner_ids:
        await ctx.send("You need to be an owner to use this command.", ephemeral=True)
        return
    
    async with aiofiles.open("managers.txt", "a", encoding="utf-8") as file:
        await file.write(f"{user.id}\n")
    manager_ids.append(user.id)
    await ctx.send(f"Added {user.mention} as a manager")
