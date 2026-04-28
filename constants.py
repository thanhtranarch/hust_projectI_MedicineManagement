import os
import darkdetect

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(CURRENT_DIR, "icon")
ICON_FILE = "app_icon_dark.png" if darkdetect.isDark() else "app_icon_light.png"
ICON_PATH = os.path.join(ICON_DIR, ICON_FILE)
