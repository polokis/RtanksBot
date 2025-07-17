import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict, List, Any
import asyncio
from config import *
from utils import *
from rank_system import get_rank_from_xp, get_rank_progress

class RTanksScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
    
    async def get_player_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Scrape player profile from RTanks ratings website."""
        try:
            url = f"{RTANKS_USER_URL}/{username}"
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.session.get(url, timeout=REQUEST_TIMEOUT)
            )
            
            if response.status_code != 200:
                return None
            
            # Check if we were redirected to homepage (player not found)
            if response.url.endswith('/') and not response.url.endswith(f'/user/{username}'):
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse player profile data
            profile_data = self._parse_player_profile(soup)
            
            if profile_data:
                profile_data['username'] = username
                profile_data['profile_url'] = url
            
            return profile_data
            
        except Exception as e:
            print(f"Error scraping player profile for {username}: {e}")
            return None
    
    def _parse_player_profile(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Parse player profile data from HTML."""
        try:
            # Check if this is a redirect page (player not found)
            if "Found. Redirecting to /" in soup.get_text():
                return None
                
            # Find player name and rank - look for the stats container
            stats_container = soup.find('div', class_='stats container')
            if not stats_container:
                return None
            
            # Find player name - it's in a bold font tag next to the rank image
            name_font = stats_container.find('font', style=re.compile(r'font-weight:\s*bold'))
            if not name_font:
                return None
                
            player_name = name_font.get_text(strip=True)
            
            # Find experience/rank progress
            experience_info = self._find_experience_info(soup)
            
            # Determine rank based on XP
            current_xp = experience_info.get('current_xp', 0)
            rank = get_rank_from_xp(current_xp)
            rank_progress = get_rank_progress(current_xp)
            
            # Find leaderboard positions
            leaderboard_positions = self._find_leaderboard_positions(soup)
            
            # Find personal statistics
            personal_stats = self._find_personal_stats(soup)
            
            # Find equipment info
            equipment = self._find_equipment_info(soup)
            
            # Check for premium status
            premium_status = self._check_premium_status(soup)
            
            # Find group/clan info
            group_info = self._find_group_info(soup)
            
            return {
                'name': player_name,
                'rank': rank,
                'experience': rank_progress,
                'leaderboard_positions': leaderboard_positions,
                'personal_stats': personal_stats,
                'equipment': equipment,
                'premium': premium_status,
                'group': group_info
            }
            
        except Exception as e:
            print(f"Error parsing player profile: {e}")
            return None
    
    def _find_experience_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Find experience and rank progress information."""
        try:
            # Look for the text_xp div that contains the XP progress
            text_xp_div = soup.find('div', class_='text_xp')
            
            if text_xp_div:
                progress_text = text_xp_div.get_text(strip=True)
                
                # Parse current XP and required XP from text like "125 919 / 156 000"
                match = re.search(r'(\d+(?:\s+\d+)*)\s*/\s*(\d+(?:\s+\d+)*)', progress_text)
                if match:
                    current_xp = parse_number(match.group(1))
                    required_xp = parse_number(match.group(2))
                    
                    return {
                        'current_xp': current_xp,
                        'required_xp': required_xp,
                        'progress_text': progress_text
                    }
            
            return {
                'current_xp': 0,
                'required_xp': 0,
                'progress_text': 'Unknown'
            }
            
        except Exception as e:
            print(f"Error finding experience info: {e}")
            return {'current_xp': 0, 'required_xp': 0, 'progress_text': 'Unknown'}
    
    def _find_leaderboard_positions(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Find current leaderboard positions."""
        try:
            positions = {}
            
            # Look for leaderboard table
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        category = cells[0].get_text(strip=True)
                        position = cells[1].get_text(strip=True)
                        value = cells[2].get_text(strip=True)
                        
                        # Map Russian categories to English
                        category_mapping = {
                            'По опыту': 'experience',
                            'Голдоловов': 'goldboxes',
                            'По киллам': 'kills',
                            'По эффективности': 'efficiency',
                            'По кристаллам': 'crystals'
                        }
                        
                        eng_category = category_mapping.get(category, category.lower())
                        positions[eng_category] = {
                            'position': position,
                            'value': value
                        }
            
            return positions
            
        except Exception as e:
            print(f"Error finding leaderboard positions: {e}")
            return {}
    
    def _find_personal_stats(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Find personal statistics like kills, deaths, KD ratio."""
        try:
            stats = {}
            
            # Look for tables containing personal statistics
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        # Map Russian stats to English
                        if 'Уничтожил' in key:
                            stats['kills'] = parse_number(value)
                        elif 'Подбит' in key:
                            stats['deaths'] = parse_number(value)
                        elif 'У/П' in key:
                            try:
                                stats['kd_ratio'] = float(value.replace(',', '.'))
                            except ValueError:
                                stats['kd_ratio'] = 0.0
                        elif 'золотых ящиков' in key:
                            stats['goldboxes'] = parse_number(value)
                        elif 'Группа' in key:
                            stats['group'] = translate_russian_to_english(value)
                        elif 'Премиум' in key:
                            stats['premium'] = 'Да' in value
            
            return stats
            
        except Exception as e:
            print(f"Error finding personal stats: {e}")
            return {}
    
    def _find_equipment_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Find currently equipped items."""
        try:
            equipment = {
                'turret': None,
                'hull': None,
                'paint': None,
                'resistances': []
            }
            
            # Look for equipment sections
            # Equipment items are typically shown with "Установленный: Да"
            equipment_sections = soup.find_all('div', class_=re.compile(r'equipment|item'))
            
            for section in equipment_sections:
                if 'Установленный' in section.get_text():
                    if 'Да' in section.get_text():
                        # This item is equipped
                        item_name = section.find('h3') or section.find('h4')
                        if item_name:
                            name = parse_equipment_name(item_name.get_text(strip=True))
                            
                            # Translate and determine equipment type based on name
                            translated_name = translate_russian_to_english(name)
                            if any(turret in translated_name.lower() for turret in ['freeze', 'smoky', 'isida', 'hammer', 'twins', 'flamethrower']):
                                equipment['turret'] = translated_name
                            elif any(hull in translated_name.lower() for hull in ['hunter', 'wasp', 'dictator', 'titan', 'viking', 'hornet']):
                                equipment['hull'] = translated_name
                            elif any(resist in translated_name.lower() for resist in ['dolphin', 'ocelot', 'badger', 'wolf', 'panther']):
                                equipment['resistances'].append(translated_name)
            
            # Look for paint (colormap) - typically has "Установленный: Да"
            paint_sections = soup.find_all(string=re.compile(r'Фотон|Граффити|Ирбис|Атом'))
            for paint_section in paint_sections:
                parent = paint_section.parent
                if parent and 'Установленный' in parent.get_text() and 'Да' in parent.get_text():
                    equipment['paint'] = translate_russian_to_english(paint_section.strip())
                    break
            
            return equipment
            
        except Exception as e:
            print(f"Error finding equipment info: {e}")
            return {'turret': None, 'hull': None, 'paint': None, 'resistances': []}
    
    def _check_premium_status(self, soup: BeautifulSoup) -> bool:
        """Check if player has premium status."""
        try:
            # Look for premium status in personal stats
            premium_text = soup.find(string=re.compile(r'Премиум'))
            if premium_text:
                parent = premium_text.parent
                if parent:
                    return 'Да' in parent.get_text()
            
            return False
            
        except Exception as e:
            print(f"Error checking premium status: {e}")
            return False
    
    def _find_group_info(self, soup: BeautifulSoup) -> str:
        """Find group/clan information."""
        try:
            # Look for group information
            group_text = soup.find(string=re.compile(r'Группа'))
            if group_text:
                parent = group_text.parent
                if parent:
                    # Find the value cell
                    next_cell = parent.find_next_sibling('td')
                    if next_cell:
                        return translate_russian_to_english(next_cell.get_text(strip=True))
            
            return "No Group"
            
        except Exception as e:
            print(f"Error finding group info: {e}")
            return "No Group"
    
    async def get_leaderboard(self, category: str = "experience", page: int = 1) -> Optional[Dict[str, Any]]:
        """Get leaderboard data for specified category and page."""
        try:
            # Calculate offset for pagination (10 players per page)
            offset = (page - 1) * 10
            
            # RTanks shows top 100 by default, we'll parse and paginate
            url = RTANKS_LEADERBOARD_URL
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.get(url, timeout=REQUEST_TIMEOUT)
            )
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse leaderboard data
            leaderboard_data = self._parse_leaderboard(soup, category)
            
            if not leaderboard_data:
                return None
            
            # Apply pagination
            players = leaderboard_data['players']
            total_players = len(players)
            
            start_idx = offset
            end_idx = min(start_idx + 10, total_players)
            
            paginated_players = players[start_idx:end_idx]
            
            return {
                'category': category,
                'page': page,
                'total_pages': (total_players + 9) // 10,  # Ceiling division
                'total_players': total_players,
                'players': paginated_players,
                'has_next': end_idx < total_players,
                'has_previous': page > 1
            }
            
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return None
    
    def _parse_leaderboard(self, soup: BeautifulSoup, category: str) -> Optional[Dict[str, Any]]:
        """Parse leaderboard data from HTML."""
        try:
            players = []
            
            # Map category to Russian text to find the right table
            category_text_map = {
                'experience': 'по заработанному опыту',
                'crystals': 'по заработанным кристаллам',
                'kills': 'по убийствам',
                'goldboxes': 'по пойманным голдам'
            }
            
            target_text = category_text_map.get(category, 'по заработанному опыту')
            
            # Find the container with the specific category text
            target_container = None
            containers = soup.find_all('div', class_='container')
            
            for container in containers:
                if target_text in container.get_text():
                    target_container = container
                    break
            
            if not target_container:
                # Fallback to first table if specific category not found
                target_container = soup
            
            # Find the table within the target container
            table = target_container.find('table')
            if not table:
                return None
            
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # Extract position
                    position = cells[0].get_text(strip=True)
                    
                    # Extract player info from second cell
                    player_cell = cells[1]
                    player_link = player_cell.find('a')
                    player_img = player_cell.find('img')
                    
                    if player_link and player_img:
                        player_name = player_link.get_text(strip=True)
                        player_url = player_link.get('href', '')
                        rank = parse_rank_from_image(player_img.get('src', ''))
                        
                        # Extract value from third cell
                        value = parse_number(cells[2].get_text(strip=True))
                        
                        players.append({
                            'position': int(position) if position.isdigit() else 0,
                            'name': player_name,
                            'rank': rank,
                            'value': value,
                            'profile_url': f"{RTANKS_BASE_URL}{player_url}" if player_url else None
                        })
            
            return {
                'category': category,
                'players': players
            }
            
        except Exception as e:
            print(f"Error parsing leaderboard: {e}")
            return None
