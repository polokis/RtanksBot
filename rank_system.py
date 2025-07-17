"""
RTanks rank system based on XP thresholds.
This system determines ranks based on experience points.
"""

# XP thresholds for each rank (from the official RTanks rank system)
RANK_XP_THRESHOLDS = [
    (0, "recruit"),
    (100, "private"),
    (500, "gefreiter"),
    (1500, "corporal"),
    (3700, "master-corporal"),
    (7100, "sergeant"),
    (12300, "staff-sergeant"),
    (20000, "master-sergeant"),
    (29000, "first-sergeant"),
    (41000, "sergeant-major"),
    (57000, "warrant-officer-1"),
    (76000, "chief-warrant-officer-2"),
    (98000, "chief-warrant-officer-3"),
    (125000, "chief-warrant-officer-4"),
    (156000, "chief-warrant-officer-5"),
    (192000, "third-lieutenant"),
    (233000, "second-lieutenant"),
    (280000, "first-lieutenant"),
    (332000, "captain"),
    (390000, "major"),
    (455000, "lieutenant-colonel"),
    (527000, "colonel"),
    (606000, "brigadier"),
    (692000, "major-general"),
    (787000, "lieutenant-general"),
    (889000, "general"),
    (1000000, "marshal"),
    (1122000, "field-marshal"),
    (1255000, "commander"),
    (1400000, "generalissimo"),
    (1600000, "legend-premium")
]

def get_rank_from_xp(xp: int) -> str:
    """Get rank based on XP amount."""
    if xp < 0:
        return "recruit"
    
    # Find the highest rank threshold that the XP meets
    current_rank = "recruit"
    for threshold, rank in RANK_XP_THRESHOLDS:
        if xp >= threshold:
            current_rank = rank
        else:
            break
    
    return current_rank

def get_rank_progress(xp: int) -> dict:
    """Get current rank and progress to next rank."""
    current_rank = get_rank_from_xp(xp)
    
    # Find current and next thresholds
    current_threshold = 0
    next_threshold = None
    next_rank = None
    
    for i, (threshold, rank) in enumerate(RANK_XP_THRESHOLDS):
        if rank == current_rank:
            current_threshold = threshold
            # Get next rank if exists
            if i < len(RANK_XP_THRESHOLDS) - 1:
                next_threshold = RANK_XP_THRESHOLDS[i + 1][0]
                next_rank = RANK_XP_THRESHOLDS[i + 1][1]
            break
    
    return {
        'current_rank': current_rank,
        'current_xp': xp,
        'current_threshold': current_threshold,
        'next_threshold': next_threshold,
        'next_rank': next_rank,
        'progress_text': f"{xp:,} / {next_threshold:,}" if next_threshold else f"{xp:,} (Max Rank)"
    }