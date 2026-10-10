# Foreground ANSI colors
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'

# Background ANSI colors
BG_BLACK = '\033[40m'
BG_BLUE = '\033[44m'

# Reset code
RESET = '\033[0m'

mapper = {
    BG_BLACK + RED: "#ff4d4f",
    BG_BLACK + GREEN: "#52c41a",
    BG_BLACK + YELLOW: "#fadb14",
    BG_BLACK + BLUE: "#1890ff",
    BG_BLACK + MAGENTA: "#eb2f96",
    BG_BLACK + CYAN: "#13c2c2",
    BG_BLACK + WHITE: "#e6f7ff",
    BG_BLUE + WHITE: "#fa8c16"
}

def reformat(message: str) -> str:
    """
    Mengonversi string log ANSI terminal menjadi string berformat HTML warna rapi.
    """
    for key, value in mapper.items():
        message = message.replace(key, f'<span style="color: {value}; font-weight: 500;">')
    message = message.replace(RESET, '</span>')
    return message
