# Third-party imports
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
        "Light Blue": "&H00FF8080",
        "Dark Blue": "&H008B0000",
        "Light Green": "&H0090EE90",
        "Dark Green": "&H00006400",
        "Light Red": "&H008080FF",
        "Dark Red": "&H0000008B",
        "Light Gray": "&H00D3D3D3",
        "Dark Gray": "&H00404040",
        "Gold": "&H0000D7FF",
        "Silver": "&H00C0C0C0",
        "Beige": "&H00DCF5F5",
        "Maroon": "&H00000080",
        "Olive": "&H00008080",
        "Navy": "&H00800000",
        "Teal": "&H00808000",
        "Turquoise": "&H00D0E040",
        "Violet": "&H00EE82EE",
        "Indigo": "&H004B0082",
        "Coral": "&H00507FFF",
    }

def is_valid_ass_color(color: str) -> bool:
    return color.startswith("&H") and len(color) == 10

def validate_and_get_color(color: str, default_color: str, available_colors: dict) -> str:
    if is_valid_ass_color(color):
        return color
    return available_colors.get(color, default_color)