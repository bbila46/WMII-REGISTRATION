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
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Server and role settings
SERVER_ID = 1387102987238768783
ROLE_ID = 1392653369964757154
LOG_CHANNEL_ID = 1392655742430871754
WELCOME_CHANNEL_ID = 1387102987238768788
INVITE_LINK = "https://discord.gg/beX6REQH"
WELCOME_GIF_URL = "https://www.dropbox.com/scl/fi/yxya94d102ltsrz64qv9k/Photo-Jul-16-2025-22-48-40.gif?rlkey=1bs2wfc8ae0tuax8deyo6crwy&st=lqux5oe7&raw=1"

# Temporary user-role storage
user_role_choices = {}

# Modal: Registration
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

        # Role embed
        role_embed = discord.Embed(
            title="Choose Your Role",
            description="Click the button below to select your role.",
            color=discord.Color.from_str("#B19CD9")
        )
        view = RoleView(interaction.user.id)
        await interaction.response.send_message(embed=role_embed, view=view, ephemeral=True)

        # Log embed
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
                color=discord.Color.from_str("#7D5BA6")
            )
            await log_channel.send(embed=log_embed)

# Role button
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
                    f"✨ Join **Wisteria Medical Institute**: {INVITE_LINK}"
                ),
                color=discord.Color.from_str("#C9A0DC")
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("This button is not for you!", ephemeral=True)

# Role view
class RoleView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.add_item(RoleButton(user_id))

# Ready event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Command sync failed: {e}")

# Member join event
@bot.event
async def on_member_join(member: discord.Member):
    role_id = user_role_choices.get(member.id)
    if role_id:
        role = member.guild.get_role(role_id)
        if role:
            try:
                await member.add_roles(role)
                print(f"Assigned {role.name} to {member.name}")
            except Exception as e:
                print(f"Role assignment failed: {e}")
        user_role_choices.pop(member.id, None)

    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🌸 Welcome to Wisteria Medical Institute 🌸",
            description=(
                f"Greetings, <@{member.id}>!\n\n"
                "We’re thrilled to welcome you to **Wisteria Medical Institute** — where knowledge meets compassion.\n\n"
                "Thank you for choosing us as your academic home. Here, you'll grow, learn, and shape the future "
                "of medicine with a supportive and passionate community.\n\n"
                "💡 Need help? Just ask. You’re never alone here!\n\n"
                "🌿 **Join here to complete your registration**:\n"
                f"🔗 {INVITE_LINK}"
            ),
            color=discord.Color.from_str("#B19CD9")
        )
        embed.set_image(url=WELCOME_GIF_URL)
        embed.set_footer(
            text="Wisteria Medical Institute",
            icon_url="https://i.imgur.com/zjXe9Rv.png"  # Optional: Replace with your own wisteria-themed icon
        )
        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Failed to send welcome: {e}")

# Slash command
@app_commands.command(name="wmi_register", description="Register for Wisteria Medical Institute")
async def wmi_register(interaction: discord.Interaction):
    await interaction.response.send_modal(RegistrationModal())

bot.tree.add_command(wmi_register)

# HTTP server
async def handle(request):
    return web.Response(text="Bot is running")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"Web server started on port {PORT}")

# Main run
async def main():
    await asyncio.gather(
        bot.start(DISCORD_TOKEN),
        start_web_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
