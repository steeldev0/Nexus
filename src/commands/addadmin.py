@bot.slash_command(description="Adds a user as an admin")
async def addadmin(interaction, user_id: str):
    if interaction.user.id not in manager_ids:
        await interaction.response.send_message("You need to be a nexus manager to use this command", ephemeral=True)
        return

    try:
        user_id = int(user_id)
    except ValueError:
        await interaction.response.send_message("Put a valid user ID", ephemeral=True)
        return

    if user_id in admin_ids:
        await interaction.response.send_message("This user is already an admin", ephemeral=True)
        return

    with open("admins.txt", "a") as file:
        file.write(f"\n{user_id}")

    admin_ids.append(user_id)

    user = await interaction.client.fetch_user(user_id)
    if user:
        try:
            embed = nextcord.Embed(
                title="Nexus Moderation",
                description="You are now a Nexus admin, woohoo!",
                color=nextcord.Color.green()
            )
            await user.send(embed=embed)
        except nextcord.Forbidden:
            pass

        await interaction.response.send_message(f"User {user_id} has been added as an admin", ephemeral=True)
    else:
        await interaction.response.send_message("Failed to fetch user, try again maybe?", ephemeral=True)