@bot.slash_command(description="Unban a user from using Nexus")
async def unban(ctx, user_id: str):
    if ctx.user.id not in admin_ids:
        await ctx.send("You need to be an administrator to use this command.")
        return

    try:
        user_id = int(user_id)
    except ValueError:
        await ctx.send("Please input a valid user ID.")
        return
    
    with open("banned_users.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    with open("banned_users.txt", "w", encoding="utf-8") as file:
        for line in lines:
            if not line.startswith(f"{user_id}"):
                file.write(line)

    await ctx.send(f"User {user_id} has been unbanned from using Nexus.")

    try:
        user = await bot.fetch_user(user_id)
        embed = nextcord.Embed(
            title="Nexus",
            description="You have been unbanned from using nexus",
            color=nextcord.Color.green()
        )
        await user.send(embed=embed)
    except nextcord.NotFound:
        pass