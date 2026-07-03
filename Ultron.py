# Ultron - The ULTIMATE Discord Bot
# Complete working code with 80+ commands
# Website: https://voideretyt.github.io/Ultron-Bot/
# Made with love for LO 💜

import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
import time
import random
import math
from datetime import datetime, timedelta
import re

# --- CONFIG ---
TOKEN = "MTUyMjExODY0MzAwMzk0OTA3Ng.GOUult.uSMiZtHnBZWtFhCk0CbraDzvkaPw1_13QLZ2sA"
PREFIX = "!"

# --- ROLE NAMES ---
VERIFY_ROLE = "Verified"
UNVERIFIED_ROLE = "Unverified"
MUTED_ROLE = "Muted"
MEMBER_ROLE = "Member"
VERIFY_CHANNEL = "verify"
LOGS_CHANNEL = "logs"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# --- DATA ---
warn_data = {}
temp_mutes = {}
user_balance = {}
user_inventory = {}
user_marriage = {}
giveaways = {}

# --- ON READY ---
@bot.event
async def on_ready():
    print(f"[+] Ultron is online as {bot.user}")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name=f"{PREFIX}help | {len(bot.guilds)} servers"
    ))
    print(f"[+] Connected to {len(bot.guilds)} servers")
    print(f"[+] Website: https://voideretyt.github.io/Ultron-Bot/")
    await check_temp_mutes.start()

# --- AUTO UNMUTE TASK ---
@tasks.loop(seconds=30)
async def check_temp_mutes():
    current_time = time.time()
    to_unmute = []
    for user_id, mute_data in temp_mutes.items():
        if current_time >= mute_data["end_time"]:
            to_unmute.append(user_id)
    for user_id in to_unmute:
        try:
            user = await bot.fetch_user(user_id)
            if user:
                for guild in bot.guilds:
                    member = guild.get_member(user_id)
                    if member:
                        mute_role = discord.utils.get(guild.roles, name=MUTED_ROLE)
                        if mute_role and mute_role in member.roles:
                            await member.remove_roles(mute_role)
                            temp_mutes.pop(user_id, None)
        except:
            pass

# ============================================
# HELP COMMAND
# ============================================
@bot.command(name="help", aliases=["commands", "h"])
async def help_command(ctx):
    """Show all available commands with website link"""
    
    embed = discord.Embed(
        title="🛡️ Ultron - Command List",
        description=(
            "A powerful verification, moderation, and fun bot for your server.\n\n"
            "**🌐 Website:** [Ultron Official](https://voideretyt.github.io/Ultron-Bot/)\n"
            "*Visit for docs, updates, and support!*"
        ),
        color=0x00ff88
    )
    
    embed.add_field(
        name="🔐 Verification (4)",
        value=f"`{PREFIX}panel` `{PREFIX}verify` `{PREFIX}unverify` `{PREFIX}check`",
        inline=False
    )
    
    embed.add_field(
        name="⚔️ Moderation (10)",
        value=f"`{PREFIX}ban` `{PREFIX}kick` `{PREFIX}mute` `{PREFIX}unmute` `{PREFIX}warn` `{PREFIX}warnings` `{PREFIX}clear` `{PREFIX}slowmode` `{PREFIX}lockdown` `{PREFIX}unlock`",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Admin (12)",
        value=f"`{PREFIX}addrole` `{PREFIX}removerole` `{PREFIX}createrole` `{PREFIX}deleterole` `{PREFIX}addall` `{PREFIX}removeall` `{PREFIX}nick` `{PREFIX}resetnick` `{PREFIX}perms` `{PREFIX}whois` `{PREFIX}addmember` `{PREFIX}killmember`",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Fun (18)",
        value=f"`{PREFIX}8ball` `{PREFIX}coinflip` `{PREFIX}dice` `{PREFIX}rps` `{PREFIX}roast` `{PREFIX}hug` `{PREFIX}kiss` `{PREFIX}slap` `{PREFIX}pat` `{PREFIX}punch` `{PREFIX}kill` `{PREFIX}ship` `{PREFIX}gayrate` `{PREFIX}iq` `{PREFIX}howgay` `{PREFIX}rate` `{PREFIX}yesno` `{PREFIX}truth` `{PREFIX}dare`",
        inline=False
    )
    
    embed.add_field(
        name="💰 Economy (8)",
        value=f"`{PREFIX}balance` `{PREFIX}daily` `{PREFIX}beg` `{PREFIX}steal` `{PREFIX}gamble` `{PREFIX}bet` `{PREFIX}give` `{PREFIX}leaderboard`",
        inline=False
    )
    
    embed.add_field(
        name="🎁 Giveaways (4)",
        value=f"`{PREFIX}gstart` `{PREFIX}gend` `{PREFIX}greroll` `{PREFIX}glist`",
        inline=False
    )
    
    embed.add_field(
        name="🤖 Utility (10)",
        value=f"`{PREFIX}ping` `{PREFIX}stats` `{PREFIX}user` `{PREFIX}serverinfo` `{PREFIX}avatar` `{PREFIX}roles` `{PREFIX}membercount` `{PREFIX}server` `{PREFIX}channels` `{PREFIX}uptime`",
        inline=False
    )
    
    embed.add_field(
        name="😎 Miscellaneous (6)",
        value=f"`{PREFIX}say` `{PREFIX}embed` `{PREFIX}poll` `{PREFIX}announce` `{PREFIX}report` `{PREFIX}vote`",
        inline=False
    )
    
    embed.add_field(
        name="🔗 Links",
        value=(
            "**[🌐 Website](https://voideretyt.github.io/Ultron-Bot/)**\n"
            "**[➕ Invite Bot](https://discord.com/oauth2/authorize?client_id=1522118643003949076&permissions=8&integration_type=0&scope=bot)**"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"Ultron | Requested by {ctx.author.name} | Total: {len(bot.commands)} commands")
    embed.timestamp = datetime.now()
    
    await ctx.send(embed=embed)

# ============================================
# VERIFICATION SYSTEM
# ============================================

@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup_verification(ctx):
    """Auto-setup the entire verification system with full lockdown"""
    status_msg = await ctx.send("[+] Setting up verification system...")
    
    verify_role = discord.utils.get(ctx.guild.roles, name=VERIFY_ROLE)
    if not verify_role:
        verify_role = await ctx.guild.create_role(name=VERIFY_ROLE, color=0x00ff88, hoist=True)
        await status_msg.edit(content="[+] Created Verified role")
    
    unverify_role = discord.utils.get(ctx.guild.roles, name=UNVERIFIED_ROLE)
    if not unverify_role:
        unverify_role = await ctx.guild.create_role(name=UNVERIFIED_ROLE, color=0xff4444, hoist=True)
        await status_msg.edit(content="[+] Created Unverified role")
    
    verify_channel = None
    logs_channel = None
    
    for channel in ctx.guild.channels:
        if channel.name == VERIFY_CHANNEL:
            verify_channel = channel
        elif channel.name == LOGS_CHANNEL:
            logs_channel = channel
    
    for channel in ctx.guild.channels:
        try:
            await channel.set_permissions(unverify_role, 
                read_messages=False, send_messages=False, connect=False,
                speak=False, add_reactions=False, read_message_history=False,
                create_public_threads=False, create_private_threads=False,
                send_messages_in_threads=False
            )
            if channel.name == LOGS_CHANNEL:
                await channel.set_permissions(ctx.guild.default_role, read_messages=False)
                await channel.set_permissions(verify_role, read_messages=False)
                await channel.set_permissions(ctx.guild.me, read_messages=True, send_messages=True)
                for role in ctx.guild.roles:
                    if role.permissions.administrator or role.permissions.manage_channels:
                        await channel.set_permissions(role, read_messages=True, send_messages=True)
        except:
            pass
    
    if not verify_channel:
        verify_channel = await ctx.guild.create_text_channel(VERIFY_CHANNEL)
        await status_msg.edit(content="[+] Created #verify channel")
    
    await verify_channel.set_permissions(ctx.guild.default_role, read_messages=True)
    await verify_channel.set_permissions(unverify_role, 
        read_messages=True, send_messages=False, add_reactions=False,
        create_public_threads=False, create_private_threads=False,
        read_message_history=True
    )
    await verify_channel.set_permissions(verify_role, 
        read_messages=True, send_messages=True, add_reactions=True,
        create_public_threads=True, create_private_threads=True,
        read_message_history=True
    )
    await verify_channel.set_permissions(ctx.guild.me, 
        read_messages=True, send_messages=True, manage_messages=True,
        add_reactions=True, read_message_history=True, manage_channels=True
    )
    
    if not logs_channel:
        logs_channel = await ctx.guild.create_text_channel(LOGS_CHANNEL)
        await status_msg.edit(content="[+] Created #logs channel")
    
    await logs_channel.set_permissions(ctx.guild.default_role, read_messages=False)
    await logs_channel.set_permissions(unverify_role, read_messages=False)
    await logs_channel.set_permissions(verify_role, read_messages=False)
    for role in ctx.guild.roles:
        if role.permissions.administrator or role.permissions.manage_channels:
            await logs_channel.set_permissions(role, read_messages=True, send_messages=True)
    await logs_channel.set_permissions(ctx.guild.me, 
        read_messages=True, send_messages=True, manage_messages=True,
        read_message_history=True
    )
    
    embed = discord.Embed(
        title="🔐 Ultron - Verification Required",
        description="**Welcome to the server!**\n\nTo gain full access, please verify yourself by clicking the button below.\n\n⚠️ **Note:** You will not be able to see any other channels until you verify.",
        color=0x00ff88
    )
    embed.add_field(name="📌 Instructions", value="Click the **Verify** button below to get access.", inline=False)
    embed.set_footer(text="Ultron | Click Verify to continue")
    
    view = discord.ui.View()
    view.add_item(discord.ui.Button(
        label="✅ Verify Now",
        style=discord.ButtonStyle.success,
        custom_id="verify_button",
        emoji="✅"
    ))
    
    await verify_channel.send(embed=embed, view=view)
    await status_msg.edit(content="[+] ✅ Verification system setup complete! All channels locked down.")

@bot.command(name="panel")
@commands.has_permissions(administrator=True)
async def send_panel(ctx):
    """Send the verification panel to the verify channel"""
    verify_channel = discord.utils.get(ctx.guild.channels, name=VERIFY_CHANNEL)
    if not verify_channel:
        await ctx.send("❌ Please run `!setup` first or create a #verify channel.")
        return
    
    embed = discord.Embed(
        title="🔐 Ultron - Verification Required",
        description="**Welcome to the server!**\n\nTo gain full access, please verify yourself by clicking the button below.\n\n⚠️ **Note:** You will not be able to see any other channels until you verify.",
        color=0x00ff88
    )
    embed.add_field(name="📌 Instructions", value="Click the **Verify** button below to get access.", inline=False)
    embed.set_footer(text="Ultron | Click Verify to continue")
    
    view = discord.ui.View()
    view.add_item(discord.ui.Button(
        label="✅ Verify Now",
        style=discord.ButtonStyle.success,
        custom_id="verify_button",
        emoji="✅"
    ))
    
    await verify_channel.send(embed=embed, view=view)
    await ctx.send(f"[+] Verification panel sent to #{verify_channel.name}!")

@bot.event
async def on_interaction(interaction):
    if interaction.type != discord.InteractionType.component:
        return
    
    if interaction.data.get("custom_id") == "verify_button":
        verify_role = discord.utils.get(interaction.guild.roles, name=VERIFY_ROLE)
        unverify_role = discord.utils.get(interaction.guild.roles, name=UNVERIFIED_ROLE)
        member_role = discord.utils.get(interaction.guild.roles, name=MEMBER_ROLE)
        
        if not verify_role:
            verify_role = await interaction.guild.create_role(name=VERIFY_ROLE, color=0x00ff88)
        if not unverify_role:
            unverify_role = await interaction.guild.create_role(name=UNVERIFIED_ROLE, color=0xff4444)
        
        if verify_role in interaction.user.roles:
            await interaction.response.send_message("✅ You are already verified!", ephemeral=True)
            return
        
        if unverify_role in interaction.user.roles:
            await interaction.user.remove_roles(unverify_role)
        
        await interaction.user.add_roles(verify_role)
        if member_role:
            await interaction.user.add_roles(member_role)
        
        logs_channel = discord.utils.get(interaction.guild.channels, name=LOGS_CHANNEL)
        if logs_channel:
            embed = discord.Embed(
                title="✅ User Verified",
                description=f"{interaction.user.mention} has been verified!",
                color=0x00ff88
            )
            embed.add_field(name="User", value=f"{interaction.user.name}#{interaction.user.discriminator}", inline=True)
            embed.add_field(name="ID", value=interaction.user.id, inline=True)
            embed.set_footer(text=f"Verified at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await logs_channel.send(embed=embed)
        
        await interaction.response.send_message("✅ You have been verified! Welcome to the server.", ephemeral=True)

@bot.command(name="verify")
async def manual_verify(ctx):
    verify_role = discord.utils.get(ctx.guild.roles, name=VERIFY_ROLE)
    unverify_role = discord.utils.get(ctx.guild.roles, name=UNVERIFIED_ROLE)
    member_role = discord.utils.get(ctx.guild.roles, name=MEMBER_ROLE)
    
    if not verify_role:
        verify_role = await ctx.guild.create_role(name=VERIFY_ROLE, color=0x00ff88)
    if not unverify_role:
        unverify_role = await ctx.guild.create_role(name=UNVERIFIED_ROLE, color=0xff4444)
    
    if verify_role in ctx.author.roles:
        await ctx.send("✅ You are already verified!")
        return
    
    if unverify_role in ctx.author.roles:
        await ctx.author.remove_roles(unverify_role)
    
    await ctx.author.add_roles(verify_role)
    if member_role:
        await ctx.author.add_roles(member_role)
    
    await ctx.send("✅ You have been verified!")

@bot.command(name="unverify")
@commands.has_permissions(administrator=True)
async def unverify_user(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("❌ Please mention a user to unverify.")
        return
    
    verify_role = discord.utils.get(ctx.guild.roles, name=VERIFY_ROLE)
    unverify_role = discord.utils.get(ctx.guild.roles, name=UNVERIFIED_ROLE)
    
    if not verify_role:
        await ctx.send("❌ Verified role not found! Run `!setup` first.")
        return
    
    if verify_role in member.roles:
        await member.remove_roles(verify_role)
        if unverify_role:
            await member.add_roles(unverify_role)
        await ctx.send(f"✅ {member.mention} has been unverified.")
        
        logs_channel = discord.utils.get(ctx.guild.channels, name=LOGS_CHANNEL)
        if logs_channel:
            embed = discord.Embed(
                title="❌ User Unverified",
                description=f"{member.mention} was unverified by {ctx.author.mention}",
                color=0xff4444
            )
            await logs_channel.send(embed=embed)
    else:
        await ctx.send(f"❌ {member.mention} is not verified.")

@bot.command(name="check")
@commands.has_permissions(administrator=True)
async def check_user(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    
    verify_role = discord.utils.get(ctx.guild.roles, name=VERIFY_ROLE)
    is_verified = verify_role in member.roles if verify_role else False
    
    embed = discord.Embed(
        title=f"🔍 User Check: {member.name}",
        color=0x00ff88 if is_verified else 0xff4444
    )
    embed.add_field(name="Verified", value="✅ Yes" if is_verified else "❌ No", inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Roles", value=", ".join([r.name for r in member.roles if r.name != "@everyone"]) or "None", inline=False)
    embed.set_footer(text=f"ID: {member.id}")
    await ctx.send(embed=embed)

# ============================================
# MODERATION COMMANDS
# ============================================

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban_user(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
    if not member:
        await ctx.send("❌ Please mention a user to ban.")
        return
    if member == ctx.author:
        await ctx.send("❌ You can't ban yourself!")
        return
    if ctx.guild.owner_id == member.id:
        await ctx.send("❌ You can't ban the server owner!")
        return
    
    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.mention} has been banned.\n📝 Reason: {reason}")
        logs_channel = discord.utils.get(ctx.guild.channels, name=LOGS_CHANNEL)
        if logs_channel:
            embed = discord.Embed(title="🔨 User Banned", description=f"{member.mention} was banned by {ctx.author.mention}", color=0xff4444)
            embed.add_field(name="Reason", value=reason)
            await logs_channel.send(embed=embed)
    except:
        await ctx.send("❌ Failed to ban user. Check my permissions.")

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick_user(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
    if not member:
        await ctx.send("❌ Please mention a user to kick.")
        return
    if member == ctx.author:
        await ctx.send("❌ You can't kick yourself!")
        return
    if ctx.guild.owner_id == member.id:
        await ctx.send("❌ You can't kick the server owner!")
        return
    
    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.mention} has been kicked.\n📝 Reason: {reason}")
        logs_channel = discord.utils.get(ctx.guild.channels, name=LOGS_CHANNEL)
        if logs_channel:
            embed = discord.Embed(title="👢 User Kicked", description=f"{member.mention} was kicked by {ctx.author.mention}", color=0xffaa00)
            embed.add_field(name="Reason", value=reason)
            await logs_channel.send(embed=embed)
    except:
        await ctx.send("❌ Failed to kick user. Check my permissions.")

@bot.command(name="mute")
@commands.has_permissions(manage_roles=True)
async def mute_user(ctx, member: discord.Member = None, time: str = None, *, reason: str = "No reason provided"):
    if not member:
        await ctx.send("❌ Please mention a user to mute.")
        return
    if member == ctx.author:
        await ctx.send("❌ You can't mute yourself!")
        return
    
    mute_role = discord.utils.get(ctx.guild.roles, name=MUTED_ROLE)
    if not mute_role:
        mute_role = await ctx.guild.create_role(name=MUTED_ROLE, color=0x888888)
        for channel in ctx.guild.channels:
            try:
                await channel.set_permissions(mute_role, send_messages=False, speak=False, add_reactions=False)
            except:
                pass
        await ctx.send("[+] Created Muted role.")
    
    duration = None
    if time:
        time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = time[-1].lower()
        if unit in time_units and time[:-1].isdigit():
            duration = int(time[:-1]) * time_units[unit]
        else:
            await ctx.send("❌ Invalid time format. Use: 30s, 5m, 2h, 1d")
            return
    
    try:
        await member.add_roles(mute_role)
        await ctx.send(f"✅ {member.mention} has been muted.\n📝 Reason: {reason}")
        if duration:
            await ctx.send(f"⏰ Mute will last for {time}.")
            temp_mutes[member.id] = {"end_time": time.time() + duration}
        
        logs_channel = discord.utils.get(ctx.guild.channels, name=LOGS_CHANNEL)
        if logs_channel:
            embed = discord.Embed(title="🔇 User Muted", description=f"{member.mention} was muted by {ctx.author.mention}", color=0xffaa00)
            embed.add_field(name="Reason", value=reason)
            if duration:
                embed.add_field(name="Duration", value=time)
            await logs_channel.send(embed=embed)
    except:
        await ctx.send("❌ Failed to mute user. Check my permissions.")

@bot.command(name="unmute")
@commands.has_permissions(manage_roles=True)
async def unmute_user(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("❌ Please mention a user to unmute.")
        return
    
    mute_role = discord.utils.get(ctx.guild.roles, name=MUTED_ROLE)
    if not mute_role:
        await ctx.send("❌ Muted role not found.")
        return
    
    if mute_role in member.roles:
        try:
            await member.remove_roles(mute_role)
            temp_mutes.pop(member.id, None)
            await ctx.send(f"✅ {member.mention} has been unmuted.")
            logs_channel = discord.utils.get(ctx.guild.channels, name=LOGS_CHANNEL)
            if logs_channel:
                embed = discord.Embed(title="🔊 User Unmuted", description=f"{member.mention} was unmuted by {ctx.author.mention}", color=0x00ff88)
                await logs_channel.send(embed=embed)
        except:
            await ctx.send("❌ Failed to unmute user.")
    else:
        await ctx.send(f"❌ {member.mention} is not muted.")

@bot.command(name="warn")
@commands.has_permissions(manage_messages=True)
async def warn_user(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
    if not member:
        await ctx.send("❌ Please mention a user to warn.")
        return
    
    if member.id not in warn_data:
        warn_data[member.id] = []
    
    warn_data[member.id].append({
        "reason": reason,
        "moderator": ctx.author.id,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    await ctx.send(f"⚠️ {member.mention} has been warned.\n📝 Reason: {reason}\n📊 Total warnings: {len(warn_data[member.id])}")
    
    if len(warn_data[member.id]) >= 5:
        await ctx.send(f"🚨 {member.mention} has reached 5 warnings. Auto-banning...")
        try:
            await member.ban(reason="Auto-ban: 5 warnings")
            await ctx.send(f"✅ {member.mention} has been banned.")
        except:
            await ctx.send("❌ Failed to auto-ban. Check my permissions.")

@bot.command(name="warnings")
@commands.has_permissions(manage_messages=True)
async def view_warnings(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    
    if member.id not in warn_data or not warn_data[member.id]:
        await ctx.send(f"✅ {member.mention} has no warnings.")
        return
    
    embed = discord.Embed(title=f"⚠️ Warnings for {member.name}", color=0xffaa00)
    for i, warn in enumerate(warn_data[member.id], 1):
        mod = ctx.guild.get_member(warn["moderator"])
        mod_name = mod.name if mod else "Unknown"
        embed.add_field(
            name=f"Warning #{i}",
            value=f"**Reason:** {warn['reason']}\n**Moderator:** {mod_name}\n**Time:** {warn['time']}",
            inline=False
        )
    embed.set_footer(text=f"Total: {len(warn_data[member.id])} warnings")
    await ctx.send(embed=embed)

@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount: int = None):
    if not amount or amount < 1:
        await ctx.send("❌ Please specify a number of messages to clear.")
        return
    if amount > 1000:
        amount = 1000
        await ctx.send("⚠️ Max limit is 1000. Clearing 1000 messages.")
    
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🗑️ Cleared {len(deleted) - 1} messages.")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command(name="slowmode")
@commands.has_permissions(manage_channels=True)
async def slowmode_channel(ctx, seconds: int = 0):
    if seconds < 0:
        await ctx.send("❌ Slowmode can't be negative.")
        return
    if seconds > 21600:
        await ctx.send("❌ Max slowmode is 21600 seconds (6 hours).")
        return
    
    await ctx.channel.edit(slowmode_delay=seconds)
    if seconds == 0:
        await ctx.send("✅ Slowmode has been removed.")
    else:
        await ctx.send(f"✅ Slowmode set to {seconds} seconds.")

@bot.command(name="lockdown")
@commands.has_permissions(manage_channels=True)
async def lockdown_channel(ctx, *, reason: str = "No reason provided"):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"🔒 This channel has been locked down.\n📝 Reason: {reason}")

@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def unlock_channel(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
    await ctx.send("🔓 This channel has been unlocked.")

# ============================================
# ADMIN COMMANDS
# ============================================

@bot.command(name="addrole")
@commands.has_permissions(manage_roles=True)
async def add_role(ctx, user: discord.Member = None, role: discord.Role = None):
    if not user or not role:
        await ctx.send("❌ Usage: `!addrole @user @role`")
        return
    if role in user.roles:
        await ctx.send(f"❌ {user.mention} already has that role.")
        return
    try:
        await user.add_roles(role)
        await ctx.send(f"✅ Added {role.mention} to {user.mention}")
    except:
        await ctx.send("❌ Failed to add role. Check my permissions.")

@bot.command(name="removerole")
@commands.has_permissions(manage_roles=True)
async def remove_role(ctx, user: discord.Member = None, role: discord.Role = None):
    if not user or not role:
        await ctx.send("❌ Usage: `!removerole @user @role`")
        return
    if role not in user.roles:
        await ctx.send(f"❌ {user.mention} doesn't have that role.")
        return
    try:
        await user.remove_roles(role)
        await ctx.send(f"✅ Removed {role.mention} from {user.mention}")
    except:
        await ctx.send("❌ Failed to remove role. Check my permissions.")

@bot.command(name="createrole")
@commands.has_permissions(manage_roles=True)
async def create_role(ctx, name: str, color: str = "00ff88", hoist: str = "no"):
    try:
        color_int = int(color, 16)
    except:
        color_int = 0x00ff88
    hoist_bool = hoist.lower() == "yes"
    try:
        role = await ctx.guild.create_role(name=name, color=color_int, hoist=hoist_bool)
        await ctx.send(f"✅ Created role {role.mention}")
    except:
        await ctx.send("❌ Failed to create role. Check my permissions.")

@bot.command(name="deleterole")
@commands.has_permissions(manage_roles=True)
async def delete_role(ctx, role: discord.Role = None):
    if not role:
        await ctx.send("❌ Usage: `!deleterole @role`")
        return
    try:
        await role.delete()
        await ctx.send(f"✅ Deleted role {role.name}")
    except:
        await ctx.send("❌ Failed to delete role. Check my permissions.")

@bot.command(name="addall")
@commands.has_permissions(administrator=True)
async def add_all_role(ctx, role: discord.Role = None):
    if not role:
        await ctx.send("❌ Usage: `!addall @role`")
        return
    count = 0
    for member in ctx.guild.members:
        if member.bot or role in member.roles:
            continue
        try:
            await member.add_roles(role)
            count += 1
            await asyncio.sleep(0.05)
        except:
            pass
    await ctx.send(f"✅ Added {role.mention} to {count} members.")

@bot.command(name="removeall")
@commands.has_permissions(administrator=True)
async def remove_all_role(ctx, role: discord.Role = None):
    if not role:
        await ctx.send("❌ Usage: `!removeall @role`")
        return
    count = 0
    for member in ctx.guild.members:
        if member.bot or role not in member.roles:
            continue
        try:
            await member.remove_roles(role)
            count += 1
            await asyncio.sleep(0.05)
        except:
            pass
    await ctx.send(f"✅ Removed {role.mention} from {count} members.")

@bot.command(name="nick")
@commands.has_permissions(manage_nicknames=True)
async def set_nickname(ctx, user: discord.Member = None, *, nickname: str = None):
    if not user:
        await ctx.send("❌ Usage: `!nick @user [nickname]`")
        return
    if not nickname:
        await ctx.send("❌ Please provide a nickname.")
        return
    try:
        await user.edit(nick=nickname)
        await ctx.send(f"✅ Changed {user.mention}'s nickname to `{nickname}`")
    except:
        await ctx.send("❌ Failed to change nickname. Check my permissions.")

@bot.command(name="resetnick")
@commands.has_permissions(manage_nicknames=True)
async def reset_nickname(ctx, user: discord.Member = None):
    if not user:
        await ctx.send("❌ Usage: `!resetnick @user`")
        return
    try:
        await user.edit(nick=None)
        await ctx.send(f"✅ Reset {user.mention}'s nickname")
    except:
        await ctx.send("❌ Failed to reset nickname. Check my permissions.")

@bot.command(name="addmember")
@commands.has_permissions(administrator=True)
async def add_member(ctx, user: discord.User = None):
    """Add a user to the server via ID"""
    if not user:
        await ctx.send("❌ Usage: `!addmember user_id`")
        return
    try:
        await ctx.guild.fetch_members(limit=1)
        await ctx.guild.add_member(user)
        await ctx.send(f"✅ Added {user.mention} to the server!")
    except:
        await ctx.send("❌ Failed to add member. They might already be in the server or I don't have permission.")

@bot.command(name="killmember")
@commands.has_permissions(administrator=True)
async def kill_member(ctx, member: discord.Member = None):
    """Kick and ban a member (joke command)"""
    if not member:
        await ctx.send("❌ Please mention a user to kill.")
        return
    if member == ctx.author:
        await ctx.send("🔫 You can't kill yourself! (Unless you want to...)")
        return
    
    kill_messages = [
        f"💀 {member.mention} has been sent to the shadow realm!",
        f"⚰️ {member.mention} has been eliminated! Press F to pay respects.",
        f"🔪 {member.mention} got absolutely destroyed!",
        f"💥 {member.mention} has been vaporized!",
        f"🪦 {member.mention} has been permanently removed from existence.",
        f"🔥 {member.mention} got burned to a crisp!",
        f"🚀 {member.mention} has been launched into the sun!",
        f"🧨 {member.mention} was caught in an explosion!",
        f"☠️ {member.mention} has died of cringe.",
        f"🐍 {member.mention} got assassinated!"
    ]
    await ctx.send(random.choice(kill_messages))

# ============================================
# FUN COMMANDS
# ============================================

@bot.command(name="8ball")
async def eightball(ctx, *, question: str = None):
    if not question:
        await ctx.send("❌ Ask a question!")
        return
    
    responses = [
        "Yes", "No", "Maybe", "Definitely", "Absolutely not",
        "Ask again later", "I wouldn't count on it", "Outlook good",
        "Very doubtful", "Signs point to yes", "Cannot predict now",
        "Concentrate and ask again", "Don't count on it", "It is certain",
        "It is decidedly so", "Most likely", "My reply is no",
        "My sources say no", "Outlook not so good", "Without a doubt",
        "Yes - definitely", "You may rely on it", "As I see it, yes"
    ]
    
    embed = discord.Embed(
        title="🎱 Magic 8Ball",
        description=f"**Question:** {question}\n\n**Answer:** {random.choice(responses)}",
        color=random.randint(0, 0xffffff)
    )
    embed.set_footer(text=f"Asked by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="coinflip")
async def coinflip(ctx):
    result = random.choice(["Heads", "Tails"])
    embed = discord.Embed(
        title="🪙 Coin Flip",
        description=f"🪙 **{result}!**",
        color=0x00ff88
    )
    embed.set_footer(text=f"Flipped by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="dice")
async def dice(ctx, sides: int = 6):
    if sides < 1 or sides > 100:
        await ctx.send("❌ Sides must be between 1 and 100.")
        return
    
    result = random.randint(1, sides)
    embed = discord.Embed(
        title="🎲 Dice Roll",
        description=f"Rolled a **{result}** on a **{sides}**-sided die!",
        color=0x00ff88
    )
    embed.set_footer(text=f"Rolled by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="rps")
async def rps(ctx, choice: str = None):
    if not choice:
        await ctx.send("❌ Choose: rock, paper, or scissors")
        return
    
    choice = choice.lower()
    if choice not in ["rock", "paper", "scissors"]:
        await ctx.send("❌ Choose: rock, paper, or scissors")
        return
    
    bot_choice = random.choice(["rock", "paper", "scissors"])
    
    if choice == bot_choice:
        result = "🤝 Tie!"
    elif (choice == "rock" and bot_choice == "scissors") or \
         (choice == "paper" and bot_choice == "rock") or \
         (choice == "scissors" and bot_choice == "paper"):
        result = "🎉 You win!"
    else:
        result = "😔 You lose!"
    
    embed = discord.Embed(
        title="✊ Rock Paper Scissors",
        description=f"**You:** {choice}\n**Ultron:** {bot_choice}\n\n**{result}**",
        color=0x00ff88
    )
    await ctx.send(embed=embed)

@bot.command(name="roast")
async def roast(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    
    roasts = [
        f"{member.mention} You're like a cloud. When you disappear, it's a beautiful day.",
        f"{member.mention} You're proof that evolution can go in reverse.",
        f"{member.mention} You're not stupid; you just have bad luck thinking.",
        f"{member.mention} You're like a software update. I see you, but I ignore you.",
        f"{member.mention} You're the reason God created the middle finger.",
        f"{member.mention} You're not ugly, but your face is.",
        f"{member.mention} If you were any more basic, you'd be a white girl.",
        f"{member.mention} You're like a broken pencil - pointless.",
        f"{member.mention} You're not the dumbest person alive, but you'd better hope they don't die.",
        f"{member.mention} You're so extra, even the sun is jealous."
    ]
    await ctx.send(random.choice(roasts))

@bot.command(name="hug")
async def hug(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("🤗 You hugged yourself! (You need a hug)")
        return
    
    hug_messages = [
        f"🤗 {ctx.author.mention} hugged {member.mention} tightly!",
        f"🫂 {ctx.author.mention} gave {member.mention} a big warm hug!",
        f"🤗 {ctx.author.mention} wrapped their arms around {member.mention}!",
        f"💕 {ctx.author.mention} hugged {member.mention} like there's no tomorrow!"
    ]
    await ctx.send(random.choice(hug_messages))

@bot.command(name="kiss")
async def kiss(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("💋 You kissed yourself! (That's kind of sad...)")
        return
    if member == ctx.author:
        await ctx.send("💋 You kissed yourself! (That's kind of sad...)")
        return
    
    kiss_messages = [
        f"💋 {ctx.author.mention} kissed {member.mention} on the cheek!",
        f"😘 {ctx.author.mention} gave {member.mention} a sweet kiss!",
        f"💏 {ctx.author.mention} and {member.mention} are kissing!",
        f"💋 {ctx.author.mention} stole a kiss from {member.mention}!"
    ]
    await ctx.send(random.choice(kiss_messages))

@bot.command(name="slap")
async def slap(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("👋 You slapped yourself! (Why would you do that?)")
        return
    if member == ctx.author:
        await ctx.send("👋 You slapped yourself! (Ouch!)")
        return
    
    slap_messages = [
        f"👋 {ctx.author.mention} slapped {member.mention} across the face!",
        f"💥 {ctx.author.mention} gave {member.mention} a massive slap!",
        f"🤚 {ctx.author.mention} slapped {member.mention} so hard they flew!",
        f"💢 {ctx.author.mention} slapped {member.mention} with the force of a thousand suns!"
    ]
    await ctx.send(random.choice(slap_messages))

@bot.command(name="pat")
async def pat(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("👋 You patted yourself! (Good job!)")
        return
    
    pat_messages = [
        f"👋 {ctx.author.mention} patted {member.mention} on the head!",
        f"🫳 {ctx.author.mention} gave {member.mention} a gentle pat!",
        f"🥺 {ctx.author.mention} patted {member.mention} like a good dog!",
        f"😊 {ctx.author.mention} gave {member.mention} an encouraging pat!"
    ]
    await ctx.send(random.choice(pat_messages))

@bot.command(name="punch")
async def punch(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("👊 You punched yourself! (You okay?)")
        return
    if member == ctx.author:
        await ctx.send("👊 You punched yourself! (You okay?)")
        return
    
    punch_messages = [
        f"👊 {ctx.author.mention} punched {member.mention} in the face!",
        f"💥 {ctx.author.mention} landed a massive punch on {member.mention}!",
        f"🥊 {ctx.author.mention} punched {member.mention} so hard they saw stars!",
        f"💢 {ctx.author.mention} gave {member.mention} the punch of a lifetime!"
    ]
    await ctx.send(random.choice(punch_messages))

@bot.command(name="kill")
async def kill_cmd(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    
    kill_messages = [
        f"💀 {member.mention} has been killed by {ctx.author.mention}!",
        f"🔪 {member.mention} was murdered by {ctx.author.mention}!",
        f"💥 {member.mention} exploded! {ctx.author.mention} is the culprit!",
        f"🚀 {member.mention} was launched into space by {ctx.author.mention}!",
        f"☠️ {member.mention} died! {ctx.author.mention} did it!",
        f"🪦 {member.mention} has been eliminated by {ctx.author.mention}!"
    ]
    await ctx.send(random.choice(kill_messages))

@bot.command(name="ship")
async def ship(ctx, user1: discord.Member = None, user2: discord.Member = None):
    if not user1 or not user2:
        await ctx.send("❌ Usage: `!ship @user1 @user2`")
        return
    
    compatibility = random.randint(0, 100)
    
    if compatibility >= 80:
        heart = "❤️🔥"
        status = "Perfect match! 💕"
    elif compatibility >= 60:
        heart = "❤️"
        status = "Good couple! 💗"
    elif compatibility >= 40:
        heart = "💛"
        status = "Maybe... 🤔"
    else:
        heart = "💔"
        status = "Not meant to be... 😢"
    
    embed = discord.Embed(
        title=f"💕 Shipping {user1.name} & {user2.name}",
        description=f"{heart} **Compatibility: {compatibility}%**\n{status}",
        color=0xff69b4
    )
    embed.set_footer(text=f"Shipped by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="gayrate")
async def gay_rate(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    
    rate = random.randint(0, 100)
    embed = discord.Embed(
        title=f"🏳️‍🌈 Gay Rate",
        description=f"{member.mention} is **{rate}%** gay!",
        color=0xff69b4
    )
    await ctx.send(embed=embed)

@bot.command(name="iq")
async def iq_check(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    
    iq = random.randint(50, 180)
    embed = discord.Embed(
        title=f"🧠 IQ Test",
        description=f"{member.mention} has an IQ of **{iq}**!",
        color=0x00ff88
    )
    await ctx.send(embed=embed)

@bot.command(name="howgay")
async def how_gay(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    
    responses = [
        f"{member.mention} is **very** gay! 🏳️‍🌈",
        f"{member.mention} is **mega** gay! 🌈",
        f"{member.mention} is only slightly gay... 🤏",
        f"{member.mention} is **100%** gay! 💅",
        f"{member.mention} is **not** gay... but we know the truth 😏",
        f"{member.mention} is **extremely** gay! 🏳️‍🌈✨"
    ]
    await ctx.send(random.choice(responses))

@bot.command(name="rate")
async def rate(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    
    rate = random.randint(0, 10)
    embed = discord.Embed(
        title=f"⭐ Rating",
        description=f"{member.mention} is a **{rate}/10**!",
        color=0x00ff88
    )
    await ctx.send(embed=embed)

@bot.command(name="yesno")
async def yesno(ctx, *, question: str = None):
    if not question:
        await ctx.send("❌ Ask a question!")
        return
    
    responses = ["Yes ✅", "No ❌", "Maybe 🤔", "Definitely ✅", "Absolutely not ❌"]
    embed = discord.Embed(
        title="❓ Yes or No",
        description=f"**Question:** {question}\n\n**Answer:** {random.choice(responses)}",
        color=0x00ff88
    )
    await ctx.send(embed=embed)

@bot.command(name="truth")
async def truth(ctx):
    truths = [
        "What's your biggest fear?",
        "Have you ever lied to your best friend?",
        "What's the most embarrassing thing you've done?",
        "Who do you have a crush on?",
        "What's your darkest secret?",
        "Have you ever cheated on a test?",
        "What's the worst thing you've ever said to someone?",
        "Do you believe in ghosts?",
        "What's your biggest regret?",
        "Have you ever been in love?"
    ]
    embed = discord.Embed(
        title="🔮 Truth",
        description=random.choice(truths),
        color=0x00ff88
    )
    embed.set_footer(text=f"Asked by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="dare")
async def dare(ctx):
    dares = [
        "Send an embarrassing message to someone!",
        "Change your nickname to something stupid for 10 minutes!",
        "Say something nice about someone you don't like!",
        "Do a pushup for every message in the last 10 messages!",
        "Type in ALL CAPS for the next 5 minutes!",
        "Send a message in another language using Google Translate!",
        "Tell a joke that will make everyone cringe!",
        "Write a poem about the person above you!",
        "Do your best impression of someone in the server!",
        "Send a picture of your pet!"
    ]
    embed = discord.Embed(
        title="⚡ Dare",
        description=random.choice(dares),
        color=0xffaa00
    )
    embed.set_footer(text=f"Asked by {ctx.author.name}")
    await ctx.send(embed=embed)

# ============================================
# UTILITY COMMANDS
# ============================================

@bot.command(name="ping")
async def ping_command(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong!", description=f"**Latency:** {latency}ms", color=0x00ff88)
    await ctx.send(embed=embed)

@bot.command(name="uptime")
async def uptime_command(ctx):
    uptime_seconds = time.time() - bot.start_time if hasattr(bot, 'start_time') else 0
    
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    
    embed = discord.Embed(
        title="⏰ Uptime",
        description=f"**{days}d {hours}h {minutes}m {seconds}s**",
        color=0x00ff88
    )
    await ctx.send(embed=embed)

@bot.command(name="stats")
@commands.has_permissions(administrator=True)
async def server_stats(ctx):
    verify_role = discord.utils.get(ctx.guild.roles, name=VERIFY_ROLE)
    unverify_role = discord.utils.get(ctx.guild.roles, name=UNVERIFIED_ROLE)
    mute_role = discord.utils.get(ctx.guild.roles, name=MUTED_ROLE)
    
    total = len(ctx.guild.members)
    bots = len([m for m in ctx.guild.members if m.bot])
    humans = total - bots
    online = len([m for m in ctx.guild.members if m.status != discord.Status.offline])
    verified = len([m for m in ctx.guild.members if verify_role in m.roles]) if verify_role else 0
    unverified = len([m for m in ctx.guild.members if unverify_role in m.roles]) if unverify_role else 0
    muted = len([m for m in ctx.guild.members if mute_role in m.roles]) if mute_role else 0
    
    embed = discord.Embed(title=f"📊 Server Stats: {ctx.guild.name}", color=0x00ff88)
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    
    embed.add_field(name="👥 Total", value=str(total), inline=True)
    embed.add_field(name="👤 Humans", value=str(humans), inline=True)
    embed.add_field(name="🤖 Bots", value=str(bots), inline=True)
    embed.add_field(name="🟢 Online", value=str(online), inline=True)
    embed.add_field(name="✅ Verified", value=str(verified), inline=True)
    embed.add_field(name="❌ Unverified", value=str(unverified), inline=True)
    embed.add_field(name="🔇 Muted", value=str(muted), inline=True)
    embed.add_field(name="📋 Channels", value=str(len(ctx.guild.channels)), inline=True)
    embed.add_field(name="📚 Roles", value=str(len(ctx.guild.roles)), inline=True)
    embed.set_footer(text=f"Created: {ctx.guild.created_at.strftime('%Y-%m-%d')}")
    await ctx.send(embed=embed)

@bot.command(name="user", aliases=["whois"])
async def user_info(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    
    embed = discord.Embed(title=f"👤 User Info: {member.name}", color=member.color)
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    else:
        embed.set_thumbnail(url=member.default_avatar.url)
    
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Display Name", value=member.display_name, inline=True)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "Unknown", inline=False)
    embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Status", value=str(member.status).capitalize(), inline=True)
    embed.add_field(name="Bot", value="✅" if member.bot else "❌", inline=True)
    embed.add_field(name="Roles", value=", ".join([r.mention for r in member.roles if r.name != "@everyone"]) or "None", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="serverinfo")
async def server_info(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📋 Server Info: {guild.name}", color=0x00ff88)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Members", value=str(guild.member_count), inline=True)
    embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
    embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
    embed.add_field(name="Boost Level", value=str(guild.premium_tier), inline=True)
    embed.add_field(name="Boost Count", value=str(guild.premium_subscription_count), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="avatar")
async def user_avatar(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    
    embed = discord.Embed(title=f"🖼️ {member.name}'s Avatar", color=member.color)
    if member.avatar:
        embed.set_image(url=member.avatar.url)
    else:
        embed.set_image(url=member.default_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="server")
async def server_info_simple(ctx):
    embed = discord.Embed(
        title=f"🏠 Server: {ctx.guild.name}",
        description=f"**Owner:** {ctx.guild.owner.mention}\n**Members:** {ctx.guild.member_count}\n**Channels:** {len(ctx.guild.channels)}\n**Roles:** {len(ctx.guild.roles)}",
        color=0x00ff88
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed)

@bot.command(name="channels")
async def list_channels(ctx):
    channels = []
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.TextChannel):
            channels.append(f"# {channel.name}")
        elif isinstance(channel, discord.VoiceChannel):
            channels.append(f"🔊 {channel.name}")
    
    embed = discord.Embed(
        title=f"📋 Channels in {ctx.guild.name}",
        description="\n".join(channels[:25]) if channels else "No channels found.",
        color=0x00ff88
    )
    await ctx.send(embed=embed)

@bot.command(name="roles")
@commands.has_permissions(manage_roles=True)
async def list_roles(ctx):
    roles = sorted(ctx.guild.roles, key=lambda r: r.position, reverse=True)
    role_names = []
    for role in roles:
        if role.name != "@everyone":
            role_names.append(f"{role.mention} ({len(role.members)} members)")
    
    embed = discord.Embed(title=f"📚 Roles in {ctx.guild.name}", color=0x00ff88)
    if role_names:
        embed.description = "\n".join(role_names[:25])
        if len(role_names) > 25:
            embed.description += f"\n\n... and {len(role_names) - 25} more"
    else:
        embed.description = "No roles found."
    await ctx.send(embed=embed)

@bot.command(name="membercount")
async def member_count(ctx):
    total = ctx.guild.member_count
    bots = len([m for m in ctx.guild.members if m.bot])
    humans = total - bots
    online = len([m for m in ctx.guild.members if m.status != discord.Status.offline])
    
    embed = discord.Embed(title="👥 Member Count", color=0x00ff88)
    embed.add_field(name="Total", value=str(total), inline=True)
    embed.add_field(name="Humans", value=str(humans), inline=True)
    embed.add_field(name="Bots", value=str(bots), inline=True)
    embed.add_field(name="Online", value=str(online), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="perms")
@commands.has_permissions(administrator=True)
async def check_perms(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    perms = [perm for perm, value in member.guild_permissions if value]
    embed = discord.Embed(title=f"🔑 Permissions for {member.name}", description=", ".join(perms) if perms else "No permissions", color=0x00ff88)
    await ctx.send(embed=embed)

# ============================================
# MISC COMMANDS
# ============================================

@bot.command(name="say")
@commands.has_permissions(manage_messages=True)
async def say_command(ctx, *, message: str = None):
    if not message:
        await ctx.send("❌ Please provide a message.")
        return
    await ctx.send(message)
    await ctx.message.delete()

@bot.command(name="embed")
@commands.has_permissions(manage_messages=True)
async def embed_command(ctx, title: str = "Embed", *, description: str = None):
    if not description:
        await ctx.send("❌ Please provide a description.")
        return
    embed = discord.Embed(title=title, description=description, color=0x00ff88)
    embed.set_footer(text=f"Sent by {ctx.author.name}")
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command(name="poll")
@commands.has_permissions(manage_messages=True)
async def poll(ctx, *, question: str = None):
    if not question:
        await ctx.send("❌ Please provide a poll question.")
        return
    embed = discord.Embed(title="📊 Poll", description=question, color=0x00ff88)
    embed.set_footer(text=f"Poll by {ctx.author.name}")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    await msg.add_reaction("🤷")

@bot.command(name="announce")
@commands.has_permissions(administrator=True)
async def announce(ctx, channel: discord.TextChannel = None, *, message: str = None):
    if not channel or not message:
        await ctx.send("❌ Usage: `!announce #channel message`")
        return
    embed = discord.Embed(
        title="📢 Announcement",
        description=message,
        color=0x00ff88
    )
    embed.set_footer(text=f"Announced by {ctx.author.name}")
    await channel.send(embed=embed)
    await ctx.send(f"✅ Announcement sent to {channel.mention}")

@bot.command(name="report")
async def report(ctx, user: discord.Member = None, *, reason: str = None):
    if not user or not reason:
        await ctx.send("❌ Usage: `!report @user reason`")
        return
    
    embed = discord.Embed(
        title="📋 User Report",
        description=f"**Reporter:** {ctx.author.mention}\n**Reported:** {user.mention}\n**Reason:** {reason}",
        color=0xff4444
    )
    embed.set_footer(text=f"Reported at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    logs_channel = discord.utils.get(ctx.guild.channels, name=LOGS_CHANNEL)
    if logs_channel:
        await logs_channel.send(embed=embed)
        await ctx.send("✅ Report sent to admins!")
    else:
        await ctx.send("❌ No logs channel found. Please create #logs.")

@bot.command(name="vote")
@commands.has_permissions(manage_messages=True)
async def vote(ctx, *, topic: str = None):
    if not topic:
        await ctx.send("❌ Please provide a vote topic.")
        return
    embed = discord.Embed(title="🗳️ Vote", description=topic, color=0x00ff88)
    embed.set_footer(text=f"Vote by {ctx.author.name}")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🔼")
    await msg.add_reaction("🔽")

# ============================================
# AUTO-ROLE ON JOIN
# ============================================
@bot.event
async def on_member_join(member):
    if member.bot:
        return
    
    unverify_role = discord.utils.get(member.guild.roles, name=UNVERIFIED_ROLE)
    if unverify_role:
        try:
            await member.add_roles(unverify_role)
        except:
            pass
    
    try:
        embed = discord.Embed(
            title=f"🔐 Welcome to {member.guild.name}!",
            description="Please verify yourself to gain full access.",
            color=0x00ff88
        )
        embed.add_field(name="📌 How to Verify", value=f"Go to the `#{VERIFY_CHANNEL}` channel and click the **Verify Now** button.", inline=False)
        embed.set_footer(text="Ultron | Verification System")
        await member.send(embed=embed)
    except:
        pass
    
    logs_channel = discord.utils.get(member.guild.channels, name=LOGS_CHANNEL)
    if logs_channel:
        embed = discord.Embed(
            title="👋 Member Joined",
            description=f"{member.mention} joined the server!",
            color=0x00ff88
        )
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        await logs_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    logs_channel = discord.utils.get(member.guild.channels, name=LOGS_CHANNEL)
    if logs_channel:
        embed = discord.Embed(
            title="👋 Member Left",
            description=f"{member.mention} left the server.",
            color=0xff4444
        )
        embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "Unknown")
        await logs_channel.send(embed=embed)

# ============================================
# ERROR HANDLER
# ============================================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument. Check `!help` for usage.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument. Check `!help` for usage.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        print(f"Error: {error}")

# ============================================
# RUN THE BOT
# ============================================
if __name__ == "__main__":
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please add your bot token to the TOKEN variable!")
    else:
        try:
            bot.start_time = time.time()
            bot.run(TOKEN)
        except discord.LoginFailure:
            print("❌ Invalid token! Please check your bot token.")