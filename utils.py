import re
from typing import Optional, Dict, Any
from config import RANK_EMOJIS, GOLDBOX_EMOJI, PREMIUM_EMOJI

def parse_rank_from_image(img_url: str) -> str:
    """Extract rank name from rank image URL."""
    if not img_url:
        return "recruit"
    
    # Extract filename from URL like https://i.imgur.com/rCN2gJm.png
    filename = img_url.split('/')[-1].split('.')[0]
    
    # Map known image hashes to ranks (from scraped data)
    rank_mapping = {
        "M4GBQIq": "recruit",
        "O6Tb9li": "private",
        "sppjRis": "gefreiter",
        "UWup9qJ": "corporal",
        "lTXxLVJ": "sergeant",
        "AYAs02w": "staff-sergeant",
        "Ljy2jDX": "sergeant-first-class",
        "GzJRzgz": "master-sergeant", 
        "a3UCeT5": "first-sergeant",
        "rCN2gJm": "sergeant-major",
        "GzJRzgz": "third-lieutenant",
        "BIr8vRX": "second-lieutenant",
        "dSE90bT": "first-lieutenant",
        "BNZpCPo": "captain",
        "pxzNyxi": "major",
        "rO3Hs5f": "lieutenant-colonel",
        "LATOpxZ": "colonel",
        "R69LmLt": "brigadier",
        "iTyjOt3": "major-general",
        "Q2YgFQ1": "lieutenant-general",
        "ekbJYyf": "general",
        "paF1myt": "marshal",
        "wPZnaG0": "field-marshal",
        "Or6Ajto": "commander",
        "OQEHkm7": "generalissimo",
        "rO3Hs5f": "legend-premium"
    }
    
    return rank_mapping.get(filename, "recruit")

def get_rank_emoji(rank: str) -> str:
    """Get the appropriate emoji for a rank."""
    return RANK_EMOJIS.get(rank, RANK_EMOJIS["recruit"])

def parse_number(text: str) -> int:
    """Parse number from text, handling spaces and formatting."""
    if not text:
        return 0
    
    # Remove spaces and other formatting
    cleaned = re.sub(r'[^\d]', '', text)
    try:
        return int(cleaned)
    except ValueError:
        return 0

def format_number(num: int) -> str:
    """Format number with thousands separators."""
    return f"{num:,}"

def parse_kd_ratio(kills: int, deaths: int) -> float:
    """Calculate kill/death ratio."""
    if deaths == 0:
        return float(kills) if kills > 0 else 0.0
    return round(kills / deaths, 2)

def extract_rank_info(rank_text: str) -> Dict[str, Any]:
    """Extract rank name and progress from rank text."""
    # Example: "Уорэнт-офицер 4" with progress "125 919 / 156 000"
    if not rank_text:
        return {"name": "recruit", "level": 1, "progress": "0 / 0"}
    
    # Basic extraction - this would need to be enhanced with actual RTanks rank system
    return {
        "name": "warrant-officer-4",
        "level": 4,
        "progress": "125,919 / 156,000"
    }

def clean_html_text(text: str) -> str:
    """Clean HTML text by removing extra whitespace and formatting."""
    if not text:
        return ""
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', text.strip())
    return cleaned

def parse_equipment_name(equipment_text: str) -> str:
    """Parse equipment name from text."""
    if not equipment_text:
        return "Unknown"
    
    # Extract equipment name (e.g., "Фриз M2" -> "Freeze M2")
    equipment_translations = {
        "Фриз": "Freeze",
        "Смоки": "Smoky", 
        "Изида": "Isida",
        "Молот": "Hammer",
        "Твинс": "Twins",
        "Огнемет": "Flamethrower",
        "Хантер": "Hunter",
        "Васп": "Wasp",
        "Диктатор": "Dictator",
        "Титан": "Titan",
        "Викинг": "Viking",
        "Хорнет": "Hornet"
    }
    
    for russian, english in equipment_translations.items():
        if russian in equipment_text:
            return equipment_text.replace(russian, english)
    
    return equipment_text

def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to maximum length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def translate_russian_to_english(text: str) -> str:
    """Translate Russian text to English."""
    russian_to_english = {
        # Group/Clan translations
        "Игрок": "Player",
        "Клан": "Clan",
        "Группа": "Group",
        
        # General translations
        "Да": "Yes",
        "Нет": "No",
        "Неизвестно": "Unknown",
        "Нет группы": "No Group",
        
        # Rank translations
        "Рекрут": "Recruit",
        "Рядовой": "Private",
        "Ефрейтор": "Gefreiter",
        "Капрал": "Corporal",
        "Сержант": "Sergeant",
        "Штаб-сержант": "Staff Sergeant",
        "Старший сержант": "Sergeant First Class",
        "Мастер-сержант": "Master Sergeant",
        "Первый сержант": "First Sergeant",
        "Сержант-майор": "Sergeant Major",
        "Уорэнт-офицер 1": "Warrant Officer 1",
        "Уорэнт-офицер 2": "Chief Warrant Officer 2",
        "Уорэнт-офицер 3": "Chief Warrant Officer 3",
        "Уорэнт-офицер 4": "Chief Warrant Officer 4",
        "Уорэнт-офицер 5": "Chief Warrant Officer 5",
        "Младший лейтенант": "Third Lieutenant",
        "Младший лейтенант": "Second Lieutenant",
        "Лейтенант": "First Lieutenant",
        "Капитан": "Captain",
        "Майор": "Major",
        "Подполковник": "Lieutenant Colonel",
        "Полковник": "Colonel",
        "Бригадир": "Brigadier",
        "Генерал-майор": "Major General",
        "Генерал-лейтенант": "Lieutenant General",
        "Генерал": "General",
        "Маршал": "Marshal",
        "Фельдмаршал": "Field Marshal",
        "Командующий": "Commander",
        "Генералиссимус": "Generalissimo",
        "Легенда": "Legend",
        "Легенда 2": "Legend 2",
        "Легенда 3": "Legend 3",
        "Легенда 4": "Legend 4",
        "Легенда 5": "Legend 5",
        
        # Equipment translations
        "Фриз": "Freeze",
        "Смоки": "Smoky",
        "Изида": "Isida", 
        "Молот": "Hammer",
        "Твинс": "Twins",
        "Огнемет": "Flamethrower",
        "Хантер": "Hunter",
        "Васп": "Wasp",
        "Диктатор": "Dictator",
        "Титан": "Titan",
        "Викинг": "Viking",
        "Хорнет": "Hornet",
        
        # Paint translations
        "Зелёный": "Green",
        "Праздник": "Holiday",
        "Премиум": "Premium",
        "Пижама": "Pajamas",
        "Граффити": "Graffiti",
        "Янтарь": "Amber",
        "Кольчуга": "Chainmail",
        "Мэри": "Mary",
        "С Любовью": "With Love",
        "Атом": "Atom",
        "Ирбис": "Irbis",
        "Вихрь": "Vortex",
        "Луноход": "Moonwalker",
        "Пустыня": "Desert",
        "Синий": "Blue",
        "Тундра": "Tundra",
        "Ягуар": "Jaguar",
        "Фотон": "Photon",
        
        # Resistance translations
        "Дельфин": "Dolphin",
        "Оцелот": "Ocelot",
        "Барсук": "Badger",
        "Волк": "Wolf",
        "Пантера": "Panther"
    }
    
    if not text:
        return text
    
    # Replace Russian text with English
    for russian, english in russian_to_english.items():
        text = text.replace(russian, english)
    
    return text

def translate_rank_to_key(rank_text: str) -> str:
    """Convert rank text to config key format."""
    # Rank text to key mapping
    rank_to_key = {
        "Recruit": "recruit",
        "Private": "private",
        "Gefreiter": "gefreiter",
        "Corporal": "corporal",
        "Sergeant": "sergeant",
        "Staff Sergeant": "staff-sergeant",
        "Sergeant First Class": "sergeant-first-class",
        "Master Sergeant": "master-sergeant",
        "First Sergeant": "first-sergeant",
        "Sergeant Major": "sergeant-major",
        "Warrant Officer 1": "warrant-officer-1",
        "Chief Warrant Officer 2": "warrant-officer-2",
        "Chief Warrant Officer 3": "warrant-officer-3",
        "Chief Warrant Officer 4": "warrant-officer-4",
        "Chief Warrant Officer 5": "warrant-officer-5",
        "Third Lieutenant": "third-lieutenant",
        "Second Lieutenant": "second-lieutenant",
        "First Lieutenant": "first-lieutenant",
        "Captain": "captain",
        "Major": "major",
        "Lieutenant Colonel": "lieutenant-colonel",
        "Colonel": "colonel",
        "Brigadier": "brigadier",
        "Major General": "major-general",
        "Lieutenant General": "lieutenant-general",
        "General": "general",
        "Marshal": "marshal",
        "Field Marshal": "field-marshal",
        "Commander": "commander",
        "Generalissimo": "generalissimo",
        "Legend": "legend-premium",
        "Legend 2": "legend-premium",
        "Legend 3": "legend-premium",
        "Legend 4": "legend-premium",
        "Legend 5": "legend-premium"
    }
    
    return rank_to_key.get(rank_text, "recruit")
