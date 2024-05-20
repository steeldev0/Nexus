@bot.slash_command(description="Adds a user as an admin")
async def addadmin(interaction, user_id: str):
    if interaction.user.id not in owner_ids:
        await interaction.response.send_message("You need to be an owner to use this command.")
        return

    try:
        user_id = int(user_id)
    except ValueError:
        await interaction.response.send_message("Please provide a valid user ID.", ephemeral=True)
        return

    if user_id in admin_ids:
        await interaction.response.send_message("This user is already an admin.")
        return

    with open("admins.txt", "a") as file:
        file.write(f"\n{user_id}")

    admin_ids.append(user_id)

    user = await interaction.client.fetch_user(user_id)
    if user:
        embed = nextcord.Embed(
            title="Nexus moderation",
            description="You are now a Nexus admin, wooho!",
            color=nextcord.Color.green()
        )
        await user.send(embed=embed)
        await interaction.response.send_message(f"User {user_id} has been added as an admin.")
    else:
        await interaction.response.send_message("Failed to fetch user.")