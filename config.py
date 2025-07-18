# RTanks API Configuration
RTANKS_BASE_URL = "https://ratings.ranked-rtanks.online"
RTANKS_USER_URL = f"{RTANKS_BASE_URL}/user"
RTANKS_LEADERBOARD_URL = RTANKS_BASE_URL

# Discord Configuration
EMBED_COLOR = 0x2b2d31  # Discord dark theme color
ERROR_COLOR = 0xed4245  # Discord red color
SUCCESS_COLOR = 0x57f287  # Discord green color

# Rank emojis mapping (emoji1-emoji31 for ranks recruit to legend)
RANK_EMOJIS = {
    "recruit": "<:emoji_1:1394987021415743588>",
    "private": "<:emoji_2:1394987069088206929>", 
    "gefreiter": "<:emoji_3:1394987101941923930>",
    "corporal": "<:emoji_4:1394987134980587630>",
    "sergeant": "<:emoji_5:1394987177284468767>",
    "staff-sergeant": "<:emoji_6:1394987207583989830>",
    "sergeant-first-class": "<:emoji_7:1394987243629969581>",
    "master-sergeant": "<:emoji_8:1394987270146097202>",
    "first-sergeant": "<:emoji_9:1394987302379458591>",
    "sergeant-major": "<:emoji_10:1394987333488480256>",
    "warrant-officer-1": "<:emoji_11:1394987701048049726>",
    "chief-warrant-officer-2": "<:emoji_12:1394987730722754641>",
    "chief-warrant-officer-3": "<:emoji_13:1394987756412866632>",
    "chief-warrant-officer-4": "<:emoji_14:1394987853104156823>",
    "chief-warrant-officer-5": "<:emoji_15:1394987883760324631>",
    "third-lieutenant": "<:emoji_16:1394988524285198356>",
    "second-lieutenant": "<:emoji_17:1394988592517873775>",
    "first-lieutenant": "<:emoji_18:1394988631609049169>",
    "captain": "<:emoji_19:1394988655252078743>",
    "major": "<:emoji_20:1394988771665248286>",
    "lieutenant-colonel": "<:emoji_21:1394988797569142845>",
    "colonel": "<:emoji_22:1394988842557112331>",
    "brigadier": "<:emoji_23:1394988970110222387>",
    "major-general": "<:emoji_24:1394989066667425842>",
    "lieutenant-general": "<:emoji_25:1394989098200207410>",
    "general": "<:emoji_26:1394989131364565053>",
    "marshal": "<:emoji_27:1394989164709019708>",
    "field-marshal": "<:emoji_28:1394989205662339082>",
    "commander": "<:emoji_29:1394989245978116217>",
    "generalissimo": "<:emoji_30:1394989278005559378>",
    "legend": "<:emoji_31:1394989379642064948>"
    "legend-premium": "<:emoji_31:1394989379642064948>"
}

# Special emojis
GOLDBOX_EMOJI = "<:emoji_32:1395002503472484352>"
PREMIUM_EMOJI = "<:emoji_33:1395399425102184609>"

# Leaderboard categories
LEADERBOARD_CATEGORIES = {
    "experience": {
        "name": "Experience Earned",
        "description": "Players ranked by experience points earned"
    },
    "crystals": {
        "name": "Crystals Earned", 
        "description": "Players ranked by crystals earned"
    },
    "kills": {
        "name": "Kills",
        "description": "Players ranked by total kills"
    },

    "goldboxes": {
        "name": "Gold Boxes Caught",
        "description": "Players ranked by gold boxes caught"
    }
}

# Request configuration
REQUEST_TIMEOUT = 10
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
