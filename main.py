import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed, ButtonStyle, ui
from datetime import datetime
import os

intents = discord.Intents.default()
intents.members = True  # So we can auto-assign roles
bot = commands.Bot(command_prefix="/", intents=intents)

GUILD_ID = 1387102987238768783  # Your target server ID
WELCOME_CHANNEL_ID = 1392655742430871754
STUDENT_ROLE_ID = 1392653369964757154
INVITE_LINK = "https://discord.gg/66qx29Tf"

class RegisterModal(ui.Modal, title="WMI Registration"):
    name = ui.TextInput(label="Your Full Name", placeholder="Jane Doe", required=True)
    email = ui.TextInput(label="Your Email (optional)", placeholder="example@domain.com", required=False)

    async def on_submit(self, interaction: Interaction):
        embed = Embed(
            title="Choose Your Role",
            description="Click below to register as a **MS1 Year 1 Student**.",
            color=discord.Color.blue()
        )
        view = RoleButton(self.name.value, self.email.value)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class RoleButton(ui.View):
    def __init__(self, name, email):
        super().__init__(timeout=None)
        self.name = name
        self.email = email

    @ui.button(label="MS1 Year 1 Student", style=ButtonStyle.success)
    async def register_button(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_message(
            f"You're almost done!\nClick to join: {INVITE_LINK}", ephemeral=True
        )

        # Post registration log
        channel = bot.get_channel(WELCOME_CHANNEL_ID)
        embed = Embed(
            title="New Registration",
            description=(
                f"**Name:** {self.name}\n"
                f"**Email:** {self.email or 'N/A'}\n"
                f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                f"**Role:** MS1 Year 1 Student\n"
                f"**User:** {interaction.user.mention}"
            ),
            color=discord.Color.green()
        )
        await channel.send(embed=embed)

@bot.tree.command(name="wmi_register", description="Register at Wisteria Medical Institute")
async def wmi_register(interaction: Interaction):
    await interaction.response.send_modal(RegisterModal())

# Assign role on member join
@bot.event
async def on_member_join(member):
    if member.guild.id != GUILD_ID:
        return

    role = member.guild.get_role(STUDENT_ROLE_ID)
    if role:
        await member.add_roles(role)

    embed = Embed(
        title="🎓 Welcome to Wisteria Medical Institute!",
        description=(
            f"Greetings, {member.mention}!\n\n"
            "**We’re thrilled to welcome you to Wisteria Medical Institute — where knowledge meets compassion.**\n\n"
            "Thank you for choosing us as your academic home. Here, you'll grow, learn, and shape the future of medicine with a supportive and passionate community.\n\n"
            "💡 If you need help or have any questions, don’t hesitate to ask!\n\n"
            "*Wishing you success on your medical journey!*"
        ),
        color=discord.Color.purple()
    )
    embed.set_video(url="https://www.dropbox.com/scl/fi/m7e8xa674tc6fp8jbdhv0/Video-Jul-13-2025-00-28-27.mp4?rlkey=gshrknyj3pes86l9wfzdcui4x&st=zoiyxrl3&dl=0")
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    await channel.send(embed=embed)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Bot is ready as {bot.user}")

# For Render Deployment (optional Flask server to keep alive)
from flask import Flask
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

import threading
def run():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run).start()

# Run the bot
bot.run(os.getenv("TOKEN"))
