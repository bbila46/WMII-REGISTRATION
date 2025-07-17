import discord
from discord.ext import commands
from discord import app_commands
import os
from datetime import datetime
from dotenv import load_dotenv
from aiohttp import web
import asyncio

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PORT = int(os.getenv('PORT', 8080))  # Default to 8080 if PORT is not set

# Set up Discord bot with intents
intents = discord.Intents.default()
intents.members = True  # Enable members intent for role assignment
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix='/', intents=intents)

# Server and role IDs
SERVER_ID = 1387102987238768783
ROLE_ID = 1392653369964757154
LOG_CHANNEL_ID = 1392655742430871754
INVITE_LINK = "https://discord.gg/beX6REQH"  # Updated invite link
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
        # Store registration data
        name = self.name.value
        email = self.email.value or "Not provided"

        # Send role selection embed with button
        role_embed = discord.Embed(
            title="Choose Your Role",
            description="Click the button below to select your role.",
            color=discord.Color.green()
        )
        view = RoleView(interaction.user.id)
        await interaction.response.send_message(embed=role_embed, view=view, ephemeral=True)

        # Log registration in the specified channel
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="New Registration",
                description=f"**Name**: {name}\n**Email**: {email}\n**Date**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n**Role**: MS1 Year 1 Student",
                color=discord.Color.blue()
            )
            await log_channel.send(embed=log_embed)

# Button for role selection
class RoleButton(discord.ui.Button):
    def __init__(self, user_id: int):
        super().__init__(label="MS1 Year 1 Student", style=discord.ButtonStyle.primary)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            # Store the user's role choice
            user_role_choices[self.user_id] = ROLE_ID
            embed = discord.Embed(
                title="Role Selected!",
                description=f"You have selected the **MS1 Year 1 Student** role!\n\nJoin our server to receive it: [Click Here]({INVITE_LINK})",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("This button is not for you!", ephemeral=True)

# View for the role button
class RoleView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.add_item(RoleButton(user_id))

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# Event: Member joins the server
@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id == SERVER_ID:
        # Check if the user has a stored role choice
        role_id = user_role_choices.get(member.id)
        if role_id:
            role = member.guild.get_role(role_id)
            if role:
                await member.add_roles(role)
                # Clear the stored choice
                user_role_choices.pop(member.id, None)

        # Send welcome message
        channel = member.guild.get_channel(LOG_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="Welcome to Wisteria Medical Institute!",
                description=f"Greetings, <@{member.id}>!\n\nWe’re thrilled to welcome you to **Wisteria Medical Institute** — where knowledge meets compassion.\n\nThank you for choosing us as your academic home. Here, you'll grow, learn, and shape the future of medicine with a supportive and passionate community.\n\n💡 If you need help or have any questions, don’t hesitate to ask!\n\nWishing you success on your medical journey!",
                color=discord.Color.purple()
            )
            embed.set_footer(text="Wisteria Medical Institute")
            embed.add_field(name="Welcome Video", value=f"[Watch Here]({WELCOME_VIDEO_URL})", inline=False)
            await channel.send(embed=embed)

# Slash command: /wmi_register
@app_commands.command(name="wmi_register", description="Register for Wisteria Medical Institute")
async def wmi_register(interaction: discord.Interaction):
    await interaction.response.send_modal(RegistrationModal())

# Minimal HTTP server for Render
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

# Run both bot and web server
async def main():
    await asyncio.gather(
        bot.start(DISCORD_TOKEN),
        start_web_server()
    )

# Run the bot
bot.tree.add_command(wmi_register)
if __name__ == "__main__":
    asyncio.run(main())
