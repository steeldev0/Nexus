@bot.slash_command(description="Ban a user from using Nexus")
async def ban(ctx, user_id: str, *, reason: str):
    if ctx.user.id not in admin_ids:
        await ctx.send("You need to be an administrator to use this command.")
        return

    try:
        user_id = int(user_id)
    except ValueError:
        await ctx.send("Please input a valid user ID.")
        return
    
    try:
        user = await bot.fetch_user(user_id)
        embed = nextcord.Embed(
            title="Nexus",
            description=f"You have been banned from using nexus for the following reason: {reason}",
            color=nextcord.Color.red()
        )
        await user.send(embed=embed)
    except nextcord.NotFound:
        await ctx.send("User not found or unable to send a direct message to the user.")
        return

    with open("banned_users.txt", "a", encoding="utf-8") as file:
        file.write(f"{user_id}\n")
    
    await ctx.send(f"User {user_id} has been banned from using Nexus for the following reason: {reason}")