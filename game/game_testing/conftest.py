"""
Pytest configuration to speed up test collection.
Mocks pygame and other slow imports before test collection.
"""
import sys
from unittest.mock import MagicMock

# Mock pygame before any imports to prevent slow audio initialization
# This speeds up pytest collection significantly
_pygame_mock = MagicMock()
_pygame_mock.mixer.init.return_value = None
_pygame_mock.mixer.music.load.return_value = None
_pygame_mock.mixer.music.play.return_value = None
_pygame_mock.mixer.music.stop.return_value = None
_pygame_mock.mixer.music.unload.return_value = None
_pygame_mock.mixer.music.set_volume.return_value = None
_pygame_mock.mixer.get_init.return_value = False
_pygame_mock.mixer.quit.return_value = None

# Patch pygame in sys.modules before any game modules are imported
sys.modules['pygame'] = _pygame_mock


