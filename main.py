import discord
from discord.ext import commands
from discord import app_commands
import os
from datetime import datetime
from dotenv import load_dotenv
from aiohttp import web
import asyncio

# Load environment variables from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PORT = int(os.getenv('PORT', 8080))  # Default port if not set

# Set up Discord bot with intents
intents = discord.Intents.default()
intents.members = True  # Required for member join events and role assignment
intents.message_content = True  # Required if you want to access message content (commands, etc)

bot = commands.Bot(command_prefix='/', intents=intents)

# Replace these IDs with your actual IDs or manage dynamically
SERVER_ID = 1387102987238768783
ROLE_ID = 1392653369964757154
LOG_CHANNEL_ID = 1392655742430871754
WELCOME_CHANNEL_ID = 1387102987238768788
INVITE_LINK = "https://discord.gg/beX6REQH"
WELCOME_VIDEO_URL = "https://www.dropbox.com/scl/fi/m7e8xa674tc6fp8jbdhv0/Video-Jul-13-2025-00-28-27.mp4?rlkey=gshrknyj3pes86l9wfzdcui4x&st=zoiyxrl3&dl=0"

# Temporary storage for user role choices (user_id: role_id)
user_role_choices = {}

# Modal for registration input
class RegistrationModal(discord.ui.Modal, title="WMI Registration"):
    name = discord.ui.TextInput(
        label="Name",
        placeholder="Enter your name",
        required=True
    )
    email = discord.ui.TextInput(
        label="Email (Optional)",
        placeholder="Enter your email (optional)",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        email = self.email.value or "Not provided"

        # Send role selection embed with button
        role_embed = discord.Embed(
            title="Choose Your Role",
            description="Click the button below to select your role.",
            color=discord.Color.from_str("#B19CD9")  # Lavender Purple
        )
        view = RoleView(interaction.user.id)
        await interaction.response.send_message(embed=role_embed, view=view, ephemeral=True)

        # Log registration
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="New Registration",
                description=(
                    f"**Name**: {name}\n"
                    f"**Email**: {email}\n"
                    f"**Date**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"**Role**: MS1 Year 1 Student"
                ),
                color=discord.Color.from_str("#7D5BA6")  # Muted Violet
            )
            await log_channel.send(embed=log_embed)

# Button for role selection
class RoleButton(discord.ui.Button):
    def __init__(self, user_id: int):
        super().__init__(label="MS1 Year 1 Student", style=discord.ButtonStyle.primary)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            user_role_choices[self.user_id] = ROLE_ID
            embed = discord.Embed(
                title="Role Selected!",
                description=(
                    f"You have selected the **MS1 Year 1 Student** role!\n\n"
                    f"Join our server to receive it: [Click Here]({INVITE_LINK})"
                ),
                color=discord.Color.from_str("#C9A0DC")  # Soft Lilac
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("This button is not for you!", ephemeral=True)

# View containing the role button
class RoleView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.add_item(RoleButton(user_id))

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) with Discord.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Event: Member joins any guild the bot is in
@bot.event
async def on_member_join(member: discord.Member):
    # Assign role if previously selected
    role_id = user_role_choices.get(member.id)
    if role_id:
        role = member.guild.get_role(role_id)
        if role:
            try:
                await member.add_roles(role, reason="Role assigned after registration")
                print(f"Assigned role {role.name} to {member.name} in {member.guild.name}")
            except Exception as e:
                print(f"Failed to assign role: {e}")
        user_role_choices.pop(member.id, None)

    # Wisteria-themed welcome embed
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="Welcome to Wisteria Medical Institute!",
            description=(
                f"Greetings, <@{member.id}>!\n\n"
                "We’re thrilled to welcome you to **Wisteria Medical Institute** — where knowledge meets compassion.\n\n"
                "Thank you for choosing us as your academic home. Here, you'll grow, learn, and shape the future "
                "of medicine with a supportive and passionate community.\n\n"
                "💡 If you need help or have any questions, don’t hesitate to ask!\n\n"
                "Wishing you success on your medical journey!"
            ),
            color=discord.Color.from_str("#B19CD9")  # Lavender Purple
        )
        embed.add_field(
            name="🌸 Welcome Video 🌸",
            value=f"[Watch Here]({WELCOME_VIDEO_URL})",
            inline=False
        )
        embed.set_footer(
            text="🌿 Wisteria Medical Institute 🌿",
            icon_url="https://i.imgur.com/zjXe9Rv.png"  # Small flower icon (you can replace this)
        )
        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Failed to send welcome message: {e}")

# Slash command: /wmi_register
@app_commands.command(name="wmi_register", description="Register for Wisteria Medical Institute")
async def wmi_register(interaction: discord.Interaction):
    await interaction.response.send_modal(RegistrationModal())

bot.tree.add_command(wmi_register)

# Minimal HTTP server for hosting platforms like Render
async def handle(request):
    return web.Response(text="Discord bot is running")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"Web server running on port {PORT}")

# Run bot and web server concurrently
async def main():
    await asyncio.gather(
        bot.start(DISCORD_TOKEN),
        start_web_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
