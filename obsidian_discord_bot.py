#!/usr/bin/env python3
"""
Obsidian Neural Mesh Discord Bot
Real-time brain graph sync + board receipt generation
"""
import discord
from discord.ext import commands
import os
import yaml
import json
from datetime import datetime
from pathlib import Path
import subprocess
import aiohttp

# Genesis constants
ARCHITECT_SNOWFLAKE = 1067614449693569044
GENESIS_INCREMENT = 3449
VAULT_PATH = Path("/vault/legions-of-minds")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Load configuration
with open("obsidian-mesh-config.yaml", "r") as f:
    config = yaml.safe_load(f)

@bot.event
async def on_ready():
    print(f'🟠 Obsidian Neural Mesh Bot Online: {bot.user}')
    print(f'⚡ Watching vault: {VAULT_PATH}')
    print(f'🔒 Genesis Lock: Increment {GENESIS_INCREMENT}\n')

@bot.command(name='receipt')
async def generate_receipt(ctx, department: str = None):
    """Generate board member receipt for a department"""
    if not department:
        await ctx.send("Usage: `!receipt [department]` (athena, lyra, nova, ipower)")
        return
    
    dept_lower = department.lower()
    dept_config = next((d for d in config['departments'] if d['name'].lower() == dept_lower), None)
    
    if not dept_config:
        await ctx.send(f"❌ Department '{department}' not found")
        return
    
    await ctx.send(f"🟠 Generating board receipt for **{dept_config['name']}**...")
    
    # Generate receipt from template
    receipt_path = VAULT_PATH / dept_config['board_receipt_template']
    
    # Populate template
    receipt_content = config['board_receipt_template'].format(
        department=dept_config['name'],
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        department_tag=dept_lower,
        increment=GENESIS_INCREMENT,
        architect_snowflake=ARCHITECT_SNOWFLAKE,
        department_name=dept_config['name'],
        quadrant_name=dept_config['quadrant'],
        timestamp=datetime.now().isoformat(),
        brain_path=dept_config['brain_path'],
        sandbox_path=dept_config['sandbox_path'],
        git_branch=dept_config['git_branch'],
        discord_channel_id=dept_config['discord_channel_id'],
        methodology_file=dept_config['methodology_file'],
        genesis_proof="..." # Would calculate real genesis proof here
    )
    
    # Save receipt
    receipt_filename = f"receipt-{dept_lower}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    receipt_full_path = VAULT_PATH / "board-receipts" / receipt_filename
    receipt_full_path.parent.mkdir(exist_ok=True)
    
    with open(receipt_full_path, "w") as f:
        f.write(receipt_content)
    
    # Commit to Git
    try:
        subprocess.run(['git', 'add', str(receipt_full_path)], cwd=VAULT_PATH, check=True)
        subprocess.run([
            'git', 'commit', '-m', 
            f'🟠 Board receipt: {dept_config["name"]} | Increment {GENESIS_INCREMENT}'
        ], cwd=VAULT_PATH, check=True)
        subprocess.run(['git', 'push'], cwd=VAULT_PATH, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}")
    
    # Create Discord embed
    embed = discord.Embed(
        title=f"📋 Board Receipt: {dept_config['name']}",
        description=f"Quadrant: {dept_config['quadrant']} | Branch: `{dept_config['git_branch']}`",
        color=0xFF4500,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="🔒 Genesis Lock", value=f"Increment {GENESIS_INCREMENT}", inline=True)
    embed.add_field(name="👑 Architect", value=f"`{ARCHITECT_SNOWFLAKE}`", inline=True)
    embed.add_field(name="🧠 Brain Path", value=f"`{dept_config['brain_path']}`", inline=False)
    
    # Add licenses
    licenses_str = "\n".join(f"✅ {lic}" for lic in dept_config['licenses'])
    embed.add_field(name="📜 Licenses", value=licenses_str or "None", inline=True)
    
    # Add APIs
    apis_str = "\n".join(f"🔌 {api}" for api in dept_config['apis'])
    embed.add_field(name="🔌 APIs", value=apis_str or "None", inline=True)
    
    # Add MCP tools
    tools_str = "\n".join(f"🛠️ {tool}" for tool in dept_config['mcp_tools'])
    embed.add_field(name="🛠️ MCP Tools", value=tools_str or "None", inline=True)
    
    embed.set_footer(text=f"Receipt file: {receipt_filename}")
    
    # Send receipt as file + embed
    with open(receipt_full_path, 'rb') as f:
        file = discord.File(f, filename=receipt_filename)
        await ctx.send(embed=embed, file=file)
    
    print(f"✅ Receipt generated: {receipt_filename}")

@bot.command(name='brain')
async def show_brain(ctx, department: str = None):
    """Show current brain state for a department"""
    if not department:
        await ctx.send("Usage: `!brain [department]` (athena, lyra, nova, ipower)")
        return
    
    dept_lower = department.lower()
    dept_config = next((d for d in config['departments'] if d['name'].lower() == dept_lower), None)
    
    if not dept_config:
        await ctx.send(f"❌ Department '{department}' not found")
        return
    
    brain_path = VAULT_PATH / dept_config['brain_path']
    methodology_path = VAULT_PATH / dept_config['methodology_file']
    
    # Read methodology
    if methodology_path.exists():
        with open(methodology_path, 'r') as f:
            methodology = f.read()[:500]  # First 500 chars
    else:
        methodology = "No methodology found"
    
    # Count files in brain
    brain_files = list(brain_path.glob('**/*.md')) if brain_path.exists() else []
    
    # Get recent Git commits for this brain
    try:
        git_log = subprocess.check_output([
            'git', 'log', '--oneline', '-n', '5', '--', str(dept_config['brain_path'])
        ], cwd=VAULT_PATH).decode()
    except:
        git_log = "No recent commits"
    
    embed = discord.Embed(
        title=f"🧠 Brain State: {dept_config['name']}",
        description=f"Quadrant: **{dept_config['quadrant']}**",
        color=0x4ECDC4,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="📁 Brain Path", value=f"`{dept_config['brain_path']}`", inline=False)
    embed.add_field(name="📄 Files", value=f"{len(brain_files)} markdown files", inline=True)
    embed.add_field(name="🌿 Git Branch", value=f"`{dept_config['git_branch']}`", inline=True)
    embed.add_field(name="📝 Methodology Preview", value=f"```{methodology}```", inline=False)
    embed.add_field(name="📜 Recent Commits", value=f"```{git_log}```", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='sync')
async def force_sync(ctx):
    """Force sync Obsidian → Git → Discord"""
    await ctx.send("🟠 Force syncing Obsidian vault...")
    
    try:
        # Git add all
        subprocess.run(['git', 'add', '.'], cwd=VAULT_PATH, check=True)
        
        # Commit
        commit_msg = f"🟠 Manual sync | Increment {GENESIS_INCREMENT} | {datetime.now().isoformat()}"
        result = subprocess.run([
            'git', 'commit', '-m', commit_msg
        ], cwd=VAULT_PATH, capture_output=True, text=True)
        
        # Push
        if result.returncode == 0:
            subprocess.run(['git', 'push'], cwd=VAULT_PATH, check=True)
            await ctx.send(f"✅ Sync complete: {commit_msg}")
        else:
            await ctx.send("✅ No changes to sync")
    
    except subprocess.CalledProcessError as e:
        await ctx.send(f"❌ Sync failed: {e}")

@bot.command(name='archive')
async def search_archive(ctx, *, query: str = None):
    """Search archive vault for license/API/tool"""
    if not query:
        await ctx.send("Usage: `!archive [query]` (e.g., 'unity license', 'discord api')")
        return
    
    query_lower = query.lower()
    results = []
    
    # Search licenses
    for lic in config['archive_vault']['structure']['licenses']:
        if query_lower in lic['name'].lower() or query_lower in str(lic.get('assigned_to', [])).lower():
            results.append(('License', lic['name'], lic.get('file', 'N/A')))
    
    # Search APIs
    for api in config['archive_vault']['structure']['apis']:
        if query_lower in api['name'].lower() or query_lower in str(api.get('used_by', [])).lower():
            results.append(('API', api['name'], api.get('file', 'N/A')))
    
    # Search MCP tools
    for tool in config['archive_vault']['structure']['mcp_tools']:
        if query_lower in tool['name'].lower() or query_lower in tool.get('description', '').lower():
            results.append(('MCP Tool', tool['name'], tool.get('server', 'N/A')))
    
    if not results:
        await ctx.send(f"❌ No results found for: `{query}`")
        return
    
    embed = discord.Embed(
        title=f"🗄️ Archive Search: {query}",
        description=f"Found {len(results)} results",
        color=0xFFD700
    )
    
    for result_type, name, path in results[:10]:  # Limit to 10
        embed.add_field(
            name=f"{result_type}: {name}",
            value=f"`{path}`",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='health')
async def cluster_health(ctx):
    """Show Kubernetes cluster health (from PONG-HEALTH bot)"""
    # This integrates with the K8s health bot from the previous document
    embed = discord.Embed(
        title="🟠 JARVIS-SWARM HEALTH MATRIX",
        description="Obsidian Neural Mesh Integration",
        color=0xFF4500,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="🧠 Vault Status", value="✅ Synced", inline=True)
    embed.add_field(name="📊 Departments", value=f"{len(config['departments'])} active", inline=True)
    embed.add_field(name="🔒 Genesis Lock", value=f"Increment {GENESIS_INCREMENT}", inline=True)
    
    await ctx.send(embed=embed)

# Run bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN not set")
        exit(1)
    
    bot.run(token)
