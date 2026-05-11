import discord
from discord import app_commands
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)

# =========================
# READY EVENT
# =========================
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(e)

# =========================
# /ticket COMMAND
# =========================
@client.tree.command(name="ticket", description="Open a support ticket panel")
async def ticket(interaction: discord.Interaction):

    button = discord.ui.Button(
        label="🎫 Create Ticket",
        style=discord.ButtonStyle.green,
        custom_id="create_ticket"
    )

    view = discord.ui.View()
    view.add_item(button)

    await interaction.response.send_message(
        "Click the button below to create a ticket:",
        view=view
    )

# =========================
# BUTTON HANDLER
# =========================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        existing = discord.utils.get(guild.channels, name=f"ticket-{user.id}")
        if existing:
            await interaction.response.send_message("You already have a ticket open.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{user.id}",
            overwrites=overwrites
        )

        close_button = discord.ui.Button(
            label="🔒 Close Ticket",
            style=discord.ButtonStyle.red,
            custom_id="close_ticket"
        )

        close_view = discord.ui.View()
        close_view.add_item(close_button)

        async def close_callback(interaction2: discord.Interaction):
            await interaction2.response.send_message("Closing ticket...", ephemeral=True)
            await channel.delete()

        close_button.callback = close_callback

        await channel.send(f"Welcome {user.mention}", view=close_view)

        await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)

# keep persistent view
client.add_view(TicketView())

client.run(TOKEN)
