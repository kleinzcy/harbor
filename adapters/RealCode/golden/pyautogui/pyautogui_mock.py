"""
Mock implementation of pyautogui for testing purposes.
This module simulates pyautogui behavior without actual mouse/keyboard input.
"""

import sys
import time
import os

# Mock constants - these are mutable to match real pyautogui behavior
FAILSAFE = True
PAUSE = 0.1
MINIMUM_DURATION = 0.1
PRIMARY = 'primary'
SECONDARY = 'secondary'
LEFT = 'left'
RIGHT = 'right'
MIDDLE = 'middle'

# Mock state
_mouse_x = 0
_mouse_y = 0
_mouse_pressed = {'left': False, 'right': False, 'middle': False}
_key_pressed = {}
_screen_size = (1920, 1080)  # default screen size
_failsafe_points = [(0, 0), (0, 1080), (1920, 0), (1920, 1080)]
FAILSAFE = True
PAUSE = PAUSE

# Exception classes
class PyAutoGUIException(Exception):
    pass

class ImageNotFoundException(PyAutoGUIException):
    pass

class FailSafeException(PyAutoGUIException):
    pass

# Utility functions
def _normalizeXYArgs(x, y):
    """Normalize x, y arguments to numbers."""
    # Handle various input types
    def to_float(val):
        if isinstance(val, list):
            if len(val) == 0:
                raise ValueError('Empty list')
            val = val[0]
        if isinstance(val, str):
            # Remove whitespace
            val = val.strip()
        return float(val)
    return to_float(x), to_float(y)

def _getNumberToken(s):
    """Mock token parsing."""
    try:
        return float(s)
    except ValueError:
        raise PyAutoGUIException(f"Cannot parse number from '{s}'")

def _getQuotedStringToken(s):
    """Mock quoted string parsing."""
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    raise PyAutoGUIException(f"Not a quoted string: '{s}'")

# Mouse functions
def moveTo(x=None, y=None, duration=0.0, tween=None, logScreenshot=False, _pause=True):
    global _mouse_x, _mouse_y
    if x is None or y is None:
        raise ValueError('x and y must be provided')
    x, y = _normalizeXYArgs(x, y)
    # Check failsafe - only trigger if coordinates match a failsafe point
    if FAILSAFE and (x, y) in _failsafe_points:
        raise FailSafeException('Mouse moved to a failsafe point.')
    # Simulate movement with duration
    if duration > 0 and tween:
        # Simulate tweening by sleeping a bit
        time.sleep(min(duration, 0.01))  # short sleep for mock
    _mouse_x = x
    _mouse_y = y
    if _pause and PAUSE > 0:
        time.sleep(PAUSE)

def moveRel(xOffset=None, yOffset=None, duration=0.0, tween=None, logScreenshot=False, _pause=True):
    global _mouse_x, _mouse_y
    if xOffset is None or yOffset is None:
        raise ValueError('xOffset and yOffset must be provided')
    xOffset = float(xOffset)
    yOffset = float(yOffset)
    moveTo(_mouse_x + xOffset, _mouse_y + yOffset, duration, tween, logScreenshot, _pause)

def click(x=None, y=None, clicks=1, interval=0.0, button=LEFT, duration=0.0, logScreenshot=False, _pause=True):
    if x is not None and y is not None:
        moveTo(x, y, duration, None, logScreenshot, False)
    # Simulate click
    if _pause and PAUSE > 0:
        time.sleep(PAUSE * clicks)
    return None

def rightClick(x=None, y=None, duration=0.0, logScreenshot=False, _pause=True):
    click(x, y, 1, 0.0, RIGHT, duration, logScreenshot, _pause)

def doubleClick(x=None, y=None, interval=0.0, button=LEFT, duration=0.0, logScreenshot=False, _pause=True):
    click(x, y, 2, interval, button, duration, logScreenshot, _pause)

def tripleClick(x=None, y=None, interval=0.0, button=LEFT, duration=0.0, logScreenshot=False, _pause=True):
    click(x, y, 3, interval, button, duration, logScreenshot, _pause)

def mouseDown(x=None, y=None, button=LEFT, duration=0.0, logScreenshot=False, _pause=True):
    global _mouse_pressed
    if x is not None and y is not None:
        moveTo(x, y, duration, None, logScreenshot, False)
    _mouse_pressed[button] = True
    if _pause and PAUSE > 0:
        time.sleep(PAUSE)

def mouseUp(x=None, y=None, button=LEFT, duration=0.0, logScreenshot=False, _pause=True):
    global _mouse_pressed
    if x is not None and y is not None:
        moveTo(x, y, duration, None, logScreenshot, False)
    _mouse_pressed[button] = False
    if _pause and PAUSE > 0:
        time.sleep(PAUSE)

def dragTo(x=None, y=None, duration=0.0, button=LEFT, logScreenshot=False, _pause=True):
    global _mouse_x, _mouse_y
    if x is None or y is None:
        raise ValueError('x and y must be provided')
    x, y = _normalizeXYArgs(x, y)
    # Simulate drag
    _mouse_x = x
    _mouse_y = y
    if _pause and PAUSE > 0:
        time.sleep(PAUSE)
    return None

def dragRel(xOffset=None, yOffset=None, duration=0.0, button=LEFT, logScreenshot=False, _pause=True):
    if xOffset is None or yOffset is None:
        raise ValueError('xOffset and yOffset must be provided')
    xOffset = float(xOffset)
    yOffset = float(yOffset)
    dragTo(_mouse_x + xOffset, _mouse_y + yOffset, duration, button, logScreenshot, _pause)

def scroll(clicks, x=None, y=None, logScreenshot=False, _pause=True):
    if x is not None and y is not None:
        moveTo(x, y, 0, None, logScreenshot, False)
    # Simulate scroll
    if _pause and PAUSE > 0:
        time.sleep(PAUSE)
    return None

def hscroll(clicks, x=None, y=None, logScreenshot=False, _pause=True):
    scroll(clicks, x, y, logScreenshot, _pause)

def vscroll(clicks, x=None, y=None, logScreenshot=False, _pause=True):
    scroll(clicks, x, y, logScreenshot, _pause)

# Keyboard functions
def typewrite(message, interval=0.0, logScreenshot=False, _pause=True):
    if not isinstance(message, (str, list)):
        raise ValueError('message must be a string or list of strings')
    # Simulate typing
    total_chars = len(message) if isinstance(message, str) else len(message)
    if interval > 0:
        time.sleep(interval * total_chars)
    if _pause and PAUSE > 0:
        time.sleep(PAUSE)
    return None

def press(keys, presses=1, interval=0.0, logScreenshot=False, _pause=True):
    if isinstance(keys, str):
        keys = [keys]
    for _ in range(presses):
        for key in keys:
            _key_pressed[key] = True
            time.sleep(0.001)
            _key_pressed[key] = False
        if interval > 0:
            time.sleep(interval)
    if _pause and PAUSE > 0:
        time.sleep(PAUSE)
    return None

def keyDown(key, logScreenshot=False, _pause=True):
    _key_pressed[key] = True
    if _pause and PAUSE > 0:
        time.sleep(PAUSE)

def keyUp(key, logScreenshot=False, _pause=True):
    _key_pressed[key] = False
    if _pause and PAUSE > 0:
        time.sleep(PAUSE)

def hold(key, logScreenshot=False, _pause=True):
    keyDown(key, logScreenshot, _pause)

def hotkey(*args, **kwargs):
    # Simulate pressing multiple keys
    for key in args:
        keyDown(key, logScreenshot=False, _pause=False)
    time.sleep(0.01)
    for key in reversed(args):
        keyUp(key, logScreenshot=False, _pause=False)
    if kwargs.get('_pause', True) and PAUSE > 0:
        time.sleep(PAUSE)
    return None

def isShiftCharacter(character):
    if len(character) != 1:
        return False
    return character.isupper() or character in '~!@#$%^&*()_+{}|:"<>?'

def isValidKey(key):
    # Simple validation
    valid_keys = ['enter', 'esc', 'shift', 'ctrl', 'alt', 'tab', 'space', 'backspace',
                  'delete', 'insert', 'home', 'end', 'pageup', 'pagedown', 'up', 'down',
                  'left', 'right', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
                  'f10', 'f11', 'f12', 'capslock', 'numlock', 'scrolllock']
    return key.lower() in valid_keys or (len(key) == 1 and key.isprintable())

# Screen capture functions
def screenshot(imageFilename=None, region=None):
    # Mock screenshot - just create an empty file if filename provided
    if imageFilename:
        # Ensure directory exists
        os.makedirs(os.path.dirname(imageFilename), exist_ok=True)
        with open(imageFilename, 'wb') as f:
            f.write(b'')  # empty file
        return imageFilename
    # Return a mock image object
    class MockImage:
        def save(self, filename):
            with open(filename, 'wb') as f:
                f.write(b'')
    return MockImage()

def locateOnScreen(image, confidence=0.8, region=None, grayscale=False):
    # Mock - always return None (not found)
    return None

def locateAllOnScreen(image, confidence=0.8, region=None, grayscale=False):
    # Return empty generator
    return []

def locateCenterOnScreen(image, confidence=0.8, region=None, grayscale=False):
    return None

def pixel(x, y):
    # Return a random color
    return (255, 255, 255)

def pixelMatchesColor(x, y, expectedRGBColor, tolerance=0):
    # Mock match
    return False

def locate(needleImage, haystackImage, confidence=0.8, grayscale=False):
    return None

def locateAll(needleImage, haystackImage, confidence=0.8, grayscale=False):
    return []

def center(coords):
    if coords is None:
        return None
    left, top, width, height = coords
    return (left + width // 2, top + height // 2)

# Message box functions
def alert(text='', title='', button='OK'):
    return button

def confirm(text='', title='', buttons=['OK', 'Cancel']):
    return buttons[0]

def prompt(text='', title='', default=''):
    return default if default else ''

def password(text='', title='', default='', mask='*'):
    return default if default else ''

# Screen info functions
def size():
    return _screen_size

def position():
    return (_mouse_x, _mouse_y)

def onScreen(x, y):
    x, y = _normalizeXYArgs(x, y)
    return 0 <= x < _screen_size[0] and 0 <= y < _screen_size[1]

def getPointOnLine(x1, y1, x2, y2, n):
    """Return point n (0.0 to 1.0) along the line from (x1,y1) to (x2,y2)."""
    x = x1 + (x2 - x1) * n
    y = y1 + (y2 - y1) * n
    return (x, y)

# Point class
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iter__(self):
        yield self.x
        yield self.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Point(self.x / scalar, self.y / scalar)

    def __repr__(self):
        return f'Point(x={self.x}, y={self.y})'

# Configuration functions
def set_failsafe(enabled):
    global FAILSAFE
    FAILSAFE = enabled

def set_pause(seconds):
    global PAUSE
    PAUSE = seconds

def get_failsafe_points():
    return _failsafe_points

# Platform detection
def platform():
    if sys.platform.startswith('win'):
        return 'win32'
    elif sys.platform.startswith('darwin'):
        return 'darwin'
    elif sys.platform.startswith('linux'):
        return 'linux'
    else:
        return sys.platform

# Dependency checking
def check_dependency(module_name):
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False