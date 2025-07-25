import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from typing import Optional, Dict, Any
from rtanks_scraper import RTanksScraper
from config import *
from utils import *

class RTanksBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # ✅ This enables reading user messages

        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )

        self.scraper = RTanksScraper()

    
    async def setup_hook(self):
        """Setup hook called when bot is ready."""
        # Register slash commands
        await self.add_cog(RTanksCog(self))
        
        # Sync commands on startup
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready."""
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="RTanks battles"
            )
        )

class RTanksCog(commands.Cog):
    def __init__(self, bot: RTanksBot):
        self.bot = bot
    
    @app_commands.command(name="player", description="Get RTanks player profile")
    @app_commands.describe(username="The RTanks player username to lookup")
    async def player_command(self, interaction: discord.Interaction, username: str):
        """Get player profile from RTanks."""
        await interaction.response.defer()
        
        try:
            # Clean username
            username = username.strip()
            
            if not username:
                await interaction.followup.send(
                    embed=create_error_embed("Please provide a valid username.")
                )
                return
            
            # Scrape player data
            player_data = await self.bot.scraper.get_player_profile(username)
            
            if not player_data:
                await interaction.followup.send(
                    embed=create_error_embed(f"Player '{username}' not found or profile could not be accessed.")
                )
                return
            
            # Create player profile embed
            embed = create_player_embed(player_data)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Error in player command: {e}")
            await interaction.followup.send(
                embed=create_error_embed("An error occurred while fetching player data.")
            )

    @app_commands.command(name="leaderboard", description="Get RTanks leaderboard")
    @app_commands.describe(category="Leaderboard category to display")
    @app_commands.choices(category=[
        app_commands.Choice(name="Experience Earned", value="experience"),
        app_commands.Choice(name="Crystals Earned", value="crystals"),
        app_commands.Choice(name="Kills", value="kills"),
        app_commands.Choice(name="Gold Boxes Caught", value="goldboxes")
    ])
    async def leaderboard_command(self, interaction: discord.Interaction, category: str = "experience"):
        """Get RTanks leaderboard with pagination."""
        await interaction.response.defer()
        
        try:
            # Get leaderboard data
            leaderboard_data = await self.bot.scraper.get_leaderboard(category, page=1)
            
            if not leaderboard_data:
                await interaction.followup.send(
                    embed=create_error_embed("Could not fetch leaderboard data.")
                )
                return
            
            # Create leaderboard embed
            embed = create_leaderboard_embed(leaderboard_data)
            
            # Create pagination view
            view = LeaderboardView(self.bot.scraper, leaderboard_data)
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error in leaderboard command: {e}")
            await interaction.followup.send(
                embed=create_error_embed("An error occurred while fetching leaderboard data.")
            )

# Create bot instance
bot = RTanksBot()



class LeaderboardView(discord.ui.View):
    """View for leaderboard pagination."""
    
    def __init__(self, scraper: RTanksScraper, initial_data: Dict[str, Any]):
        super().__init__(timeout=300)  # 5 minute timeout
        self.scraper = scraper
        self.current_data = initial_data
    
    @discord.ui.button(label="<", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Previous page button."""
        await interaction.response.defer()
        
        try:
            current_page = self.current_data['page']
            
            if current_page <= 1:
                await interaction.followup.send("Already on the first page!", ephemeral=True)
                return
            
            # Get previous page
            new_data = await self.scraper.get_leaderboard(
                self.current_data['category'], 
                page=current_page - 1
            )
            
            if not new_data:
                await interaction.followup.send("Error fetching previous page.", ephemeral=True)
                return
            
            self.current_data = new_data
            
            # Update embed
            embed = create_leaderboard_embed(new_data)
            
            # Update button states
            self.update_button_states()
            
            await interaction.edit_original_response(embed=embed, view=self)
            
        except Exception as e:
            print(f"Error in previous button: {e}")
            await interaction.followup.send("An error occurred.", ephemeral=True)
    
    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Next page button."""
        await interaction.response.defer()
        
        try:
            current_page = self.current_data['page']
            
            if not self.current_data['has_next']:
                await interaction.followup.send("No more pages available!", ephemeral=True)
                return
            
            # Get next page
            new_data = await self.scraper.get_leaderboard(
                self.current_data['category'], 
                page=current_page + 1
            )
            
            if not new_data:
                await interaction.followup.send("Error fetching next page.", ephemeral=True)
                return
            
            self.current_data = new_data
            
            # Update embed
            embed = create_leaderboard_embed(new_data)
            
            # Update button states
            self.update_button_states()
            
            await interaction.edit_original_response(embed=embed, view=self)
            
        except Exception as e:
            print(f"Error in next button: {e}")
            await interaction.followup.send("An error occurred.", ephemeral=True)
    
    def update_button_states(self):
        """Update button enabled/disabled states."""
        self.previous_button.disabled = not self.current_data['has_previous']
        self.next_button.disabled = not self.current_data['has_next']
    
    async def on_timeout(self):
        """Called when view times out."""
        # Disable all buttons
        for item in self.children:
            item.disabled = True

def create_player_embed(player_data: Dict[str, Any]) -> discord.Embed:
    """Create Discord embed for player profile."""
    name = player_data.get('name', 'Unknown')
    rank = player_data.get('rank', 'recruit')
    
    # Create embed
    embed = discord.Embed(
        title=f"{get_rank_emoji(rank)} {name}",
        description=f"**Rank:** {rank.replace('-', ' ').title()}",
        color=EMBED_COLOR,
        url=player_data.get('profile_url')
    )
    
    # Add experience info
    experience = player_data.get('experience', {})
    if experience:
        next_threshold = experience.get('next_threshold')
        if next_threshold:
            embed.add_field(
                name="Experience",
                value=f"{format_number(experience.get('current_xp', 0))} / {format_number(next_threshold)}",
                inline=True
            )
        else:
            embed.add_field(
                name="Experience",
                value=f"{format_number(experience.get('current_xp', 0))} (Max Rank)",
                inline=True
            )
    
    # Add personal stats
    stats = player_data.get('personal_stats', {})
    if stats:
        kills = stats.get('kills', 0)
        deaths = stats.get('deaths', 0)
        kd_ratio = stats.get('kd_ratio', 0.0)
        
        embed.add_field(
            name="Combat Stats",
            value=f"**Kills:** {format_number(kills)}\n**Deaths:** {format_number(deaths)}\n**K/D:** {kd_ratio}",
            inline=True
        )
        
        goldboxes = stats.get('goldboxes', 0)
        premium = stats.get('premium', False)
        group = stats.get('group', 'No Group')
        
        embed.add_field(
            name="Other Stats",
            value=f"{GOLDBOX_EMOJI} **Gold Boxes:** {format_number(goldboxes)}\n{PREMIUM_EMOJI if premium else '❌'} **Premium:** {'Yes' if premium else 'No'}\n**Group:** {group}",
            inline=True
        )
    
    # Add equipment info
    equipment = player_data.get('equipment', {})
    if equipment:
        equipment_text = ""
        
        if equipment.get('turret'):
            equipment_text += f"**Turret:** {equipment['turret']}\n"
        
        if equipment.get('hull'):
            equipment_text += f"**Hull:** {equipment['hull']}\n"
        
        if equipment.get('paint'):
            equipment_text += f"**Paint:** {equipment['paint']}\n"
        
        if equipment.get('resistances'):
            equipment_text += f"**Resistances:** {', '.join(equipment['resistances'])}\n"
        
        if equipment_text:
            embed.add_field(
                name="Equipment",
                value=equipment_text.strip(),
                inline=False
            )
    
    # Leaderboard positions removed as requested by user
    
    return embed

def create_leaderboard_embed(leaderboard_data: Dict[str, Any]) -> discord.Embed:
    """Create Discord embed for leaderboard."""
    category = leaderboard_data.get('category', 'experience')
    page = leaderboard_data.get('page', 1)
    total_pages = leaderboard_data.get('total_pages', 1)
    players = leaderboard_data.get('players', [])
    
    # Get category info
    category_info = LEADERBOARD_CATEGORIES.get(category, {})
    category_name = category_info.get('name', category.title())
    
    # Create embed
    embed = discord.Embed(
        title=f"🏆 {category_name} Leaderboard",
        description=f"**Page {page} of {total_pages}**",
        color=EMBED_COLOR
    )
    
    # Add players
    leaderboard_text = ""
    for player in players:
        position = player.get('position', 0)
        name = player.get('name', 'Unknown')
        rank = player.get('rank', 'recruit')
        value = player.get('value', 0)
           

        rank_emoji = get_rank_emoji(rank)
        
        # Add special formatting for top 3
        if position == 1:
            leaderboard_text += f"🥇 **{position}.** {rank_emoji} **{name}** - {format_number(value)}\n"
        elif position == 2:
            leaderboard_text += f"🥈 **{position}.** {rank_emoji} **{name}** - {format_number(value)}\n"
        elif position == 3:
            leaderboard_text += f"🥉 **{position}.** {rank_emoji} **{name}** - {format_number(value)}\n"
        else:
            leaderboard_text += f"**{position}.** {rank_emoji} {name} - {format_number(value)}\n"
    
    if leaderboard_text:
        embed.add_field(
            name="Rankings",
            value=leaderboard_text.strip(),
            inline=False
        )
    else:
        embed.add_field(
            name="Rankings",
            value="No players found for this category.",
            inline=False
        )
    
    # Add footer
    embed.set_footer(text="RTanks Online | Use < and > buttons to navigate")
    
    return embed

def create_error_embed(message: str) -> discord.Embed:
    """Create error embed."""
    embed = discord.Embed(
        title="❌ Error",
        description=message,
        color=ERROR_COLOR
    )
    return embed

# Export the bot for main.py
RTanksBot = RTanksBot
