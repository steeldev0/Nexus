@bot.slash_command(description="Remove a user from the admin list")
async def removeadmin(interaction, user_id: str):
    if interaction.user.id not in manager_ids:
        await interaction.response.send_message("You need to be a nexus manager to use this command", ephemeral=True)
        return

    try:
        user_id = int(user_id)
    except ValueError:
        await interaction.response.send_message("Put a valid user ID", ephemeral=True)
        return

    if user_id not in admin_ids:
        await interaction.response.send_message("This user isnt an admin", ephemeral=True)
        return

    with open("admins.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    filtered_lines = [line.strip() for line in lines if int(line.strip()) != user_id]

    if len(filtered_lines) == len(lines):
        await interaction.response.send_message("This user isnt an admin", ephemeral=True)
        return

    with open("admins.txt", "w", encoding="utf-8") as file:
        for line in filtered_lines:
            file.write(line + "\n")

    admin_ids.remove(user_id)

    await interaction.response.send_message(f"User {user_id} has been removed from the admin list", ephemeral=True)

    try:
        user = await bot.fetch_user(user_id)
        if user:
            try:
                embed = nextcord.Embed(
                    title="Nexus moderation",
                    description="You have been removed from the Nexus admins.",
                    color=nextcord.Color.red()
                )
                await user.send(embed=embed)
            except nextcord.Forbidden:
                pass
    except nextcord.NotFound:
        pass