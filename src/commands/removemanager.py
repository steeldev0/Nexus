@bot.slash_command(name='removemanager', description='Remove a nexus manager')
async def remove_manager(ctx: nextcord.Interaction, user: nextcord.User):
    if ctx.user.id not in owner_ids:
        await ctx.send("You need to be an owner to use this command")
        return
    
    manager_ids.remove(user.id)
    with open("managers.txt", "w", encoding="utf-8") as file:
        for manager_id in manager_ids:
            file.write(f"{manager_id}\n")
    await ctx.send(f"Removed {user.mention} from managers")
