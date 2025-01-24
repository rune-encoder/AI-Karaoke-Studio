import matplotlib.font_manager as fm

def get_font_list():
    """Retrieve a list of unique font names."""
    fonts = [f.name for f in fm.fontManager.ttflist]
    unique_fonts = set(fonts)
    return sorted(unique_fonts)

def get_available_colors():
    """Generate a dictionary of color names and their ASS-compatible codes."""
    return {
        "White": "&H00FFFFFF",
        "Black": "&H00000000",
        "Red": "&H000000FF",
        "Green": "&H0000FF00",
        "Blue": "&H00FF0000",
        "Yellow": "&H0000FFFF",
        "Cyan": "&H00FFFF00",
        "Magenta": "&H00FF00FF",
        "Gray": "&H00808080",
        "Orange": "&H0000A5FF",
        "Pink": "&H00CBC0FF",
        "Purple": "&H00A020F0",
        "Brown": "&H002A2AA5",
        "Lime": "&H0000FF80",
    }
