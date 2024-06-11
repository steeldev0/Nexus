@bot.slash_command(name='removemanager')
async def remove_manager(ctx, user: nextcord.User):
    if ctx.author.id not in owner_ids:
        await ctx.send("You need to be an owner to use this command")
        return
    
    manager_ids.remove(user.id)
    with open("managers.txt", "w", encoding="utf-8") as file:
        for manager_id in manager_ids:
            file.write(f"{manager_id}\n")
    await ctx.send(f"Removed {user.mention} from managers")