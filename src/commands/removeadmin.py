@bot.slash_command(description="Remove a user from the admin list")
async def removeadmin(ctx, user_id: str):
    if ctx.user.id not in owner_ids:
        await ctx.send("You need to be an owner to use this command.")
        return

    try:
        user_id = int(user_id)
    except ValueError:
        await ctx.send("Please input a valid user ID.")
        return

    if user_id not in admin_ids:
        await ctx.send("This user isn't an admin.")
        return

    with open("admins.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    filtered_lines = [line.strip() for line in lines if int(line.strip()) != user_id]

    if len(filtered_lines) == len(lines):
        await ctx.send("This user isn't an admin.")
        return

    with open("admins.txt", "w", encoding="utf-8") as file:
        for line in filtered_lines:
            file.write(line + "\n")

    await ctx.send(f"User {user_id} has been removed from the admin list.")

    try:
        user = await bot.fetch_user(user_id)
        if user:
            embed = nextcord.Embed(
                title="Nexus moderation",
                description="You have been removed from the Nexus admins.",
                color=nextcord.Color.red()
            )
            await user.send(embed=embed)
    except nextcord.NotFound:
        pass