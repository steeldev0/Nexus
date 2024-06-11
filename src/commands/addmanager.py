@bot.slash_command(name='addmanager')
async def add_manager(ctx, user: nextcord.User):
    if ctx.author.id not in owner_ids:
        await ctx.send("You need to be an owner to use this command.")
        return
    
    with open("managers.txt", "a", encoding="utf-8") as file:
        file.write(f"{user.id}\n")
    manager_ids.append(user.id)
    await ctx.send(f"Added {user.mention} as a manager")