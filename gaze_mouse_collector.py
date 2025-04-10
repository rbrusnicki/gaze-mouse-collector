import cv2
import os
import time
import logging
from datetime import datetime
from pynput.mouse import Listener as MouseListener, Controller as MouseController
from pynput.keyboard import Listener as KeyboardListener
import ctypes
from ctypes import wintypes, byref, Structure, WinError, POINTER, create_unicode_buffer

# Set up logging
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "gaze_collector.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create directories for storing captured data
mouse_data_dir = "mouse_data"
keyboard_data_dir = "keyboard_data"
os.makedirs(mouse_data_dir, exist_ok=True)
os.makedirs(keyboard_data_dir, exist_ok=True)

# Initialize camera
camera = cv2.VideoCapture(0)  # 0 is typically the default camera
if not camera.isOpened():
    logging.error("Failed to open camera. Make sure it's connected properly.")
else:
    logging.info("Camera initialized successfully")

# Define Win32 structures for cursor and caret position
class POINT(Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class RECT(Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]

class GUITHREADINFO(Structure):
    _fields_ = [("cbSize", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("hwndActive", wintypes.HWND),
                ("hwndFocus", wintypes.HWND),
                ("hwndCapture", wintypes.HWND),
                ("hwndMenuOwner", wintypes.HWND),
                ("hwndMoveSize", wintypes.HWND),
                ("hwndCaret", wintypes.HWND),
                ("rcCaret", RECT)]

# Load Win32 functions
user32 = ctypes.WinDLL('user32', use_last_error=True)
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetGUIThreadInfo.argtypes = [wintypes.DWORD, ctypes.POINTER(GUITHREADINFO)]
user32.GetGUIThreadInfo.restype = wintypes.BOOL
user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(POINT)]
user32.ClientToScreen.restype = wintypes.BOOL

# Variables for tracking state
mouse_controller = MouseController()
last_caret_pos = None
caret_pos_request_time = None
throttle_time = 0.1  # Only check caret position every 100ms

# Dictionary to track which windows have working caret detection
window_caret_detection = {}

def on_click(x, y, button, pressed):
    """
    Callback function that executes when a mouse click is detected
    """
    # Only capture on mouse press, not on release
    if pressed:
        # Get current timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Capture cursor position
        cursor_position = (x, y)
        
        # Capture image from camera
        ret, frame = camera.read()
        
        if ret:
            # Save the image with cursor position in the filename
            image_path = os.path.join(mouse_data_dir, f"{timestamp}_{x}_{y}.jpg")
            cv2.imwrite(image_path, frame)
            
            message = f"Mouse click captured at {timestamp} - Position: {cursor_position}"
            print(message)
            logging.info(message)
        else:
            logging.error("Failed to capture image from camera")

def get_caret_position():
    """
    Get the text caret position using Win32 API
    Returns a tuple (x, y) or None if not available
    """
    global last_caret_pos, caret_pos_request_time
    
    # Throttle the caret position checks
    current_time = time.time()
    if caret_pos_request_time and current_time - caret_pos_request_time < throttle_time:
        return last_caret_pos
    
    caret_pos_request_time = current_time
    
    try:
        # Get the foreground window
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None
            
        # If we already know this window doesn't support caret detection, return None immediately
        if hwnd in window_caret_detection and not window_caret_detection[hwnd]:
            return None
        
        # Get thread ID of the foreground window using ctypes directly
        process_id = wintypes.DWORD()
        thread_id = user32.GetWindowThreadProcessId(hwnd, byref(process_id))
        if not thread_id:
            return None
        
        # Get GUI thread info which contains caret information
        gui_info = GUITHREADINFO()
        gui_info.cbSize = ctypes.sizeof(GUITHREADINFO)
        if not user32.GetGUIThreadInfo(thread_id, byref(gui_info)):
            return None
            
        # Check if there's a valid caret rectangle
        if (gui_info.rcCaret.right > gui_info.rcCaret.left and 
            gui_info.rcCaret.bottom > gui_info.rcCaret.top and 
            gui_info.hwndCaret):
            
            # Create a POINT for coordinate conversion
            pt = POINT()
            pt.x = gui_info.rcCaret.left
            pt.y = gui_info.rcCaret.top
            
            # Convert client coordinates to screen coordinates
            if user32.ClientToScreen(gui_info.hwndCaret, byref(pt)):
                last_caret_pos = (pt.x, pt.y)
                # Mark this window as having working caret detection
                window_caret_detection[hwnd] = True
                return last_caret_pos
        
        # If we got here, caret detection didn't work for this window
        window_caret_detection[hwnd] = False
        return None
    
    except Exception as e:
        logging.error(f"Error getting caret position: {e}")
        return None

def on_press(key):
    """
    Callback function that executes when a key is pressed
    """
    try:
        # Only proceed for character keys, not special keys
        try:
            char = key.char
            if not char or len(char) == 0:
                return
        except AttributeError:
            # Skip special keys
            return
        
        # Get current timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Get caret position
        caret_position = get_caret_position()
        
        if caret_position:
            x, y = caret_position
            
            # Capture image from camera
            ret, frame = camera.read()
            
            if ret:
                # Save the image with caret position in the filename
                image_path = os.path.join(keyboard_data_dir, f"{timestamp}_{x}_{y}.jpg")
                cv2.imwrite(image_path, frame)
                
                message = f"Key press captured at {timestamp} - Position: {caret_position} - Key: {char}"
                print(message)
                logging.info(message)
            else:
                logging.error("Failed to capture image from camera on key press")
        else:
            logging.info(f"Skipped key press capture for key: {char} - Could not detect caret position")
            
    except Exception as e:
        logging.error(f"Error in keyboard handler: {e}")

def main():
    startup_message = "Gaze, Mouse, and Keyboard Data Collector started"
    divider = "-" * len(startup_message)
    
    print(startup_message)
    print(divider)
    print("Click anywhere to capture camera image and cursor position.")
    print("Type in applications like Notepad, Word to capture camera image and caret position.")
    print("Note: Keyboard captures are skipped if caret position cannot be detected.")
    print("Press Ctrl+C in the terminal to stop the program.")
    
    logging.info(startup_message)
    logging.info("Mouse data folder: " + os.path.abspath(mouse_data_dir))
    logging.info("Keyboard data folder: " + os.path.abspath(keyboard_data_dir))
    
    # Start mouse and keyboard listeners
    mouse_listener = MouseListener(on_click=on_click)
    keyboard_listener = KeyboardListener(on_press=on_press)
    
    mouse_listener.start()
    keyboard_listener.start()
    
    logging.info("Mouse and keyboard listeners started")
    
    try:
        # Keep the main thread alive
        while mouse_listener.is_alive() and keyboard_listener.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        logging.info("Program terminated by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        # Release camera when program ends
        mouse_listener.stop()
        keyboard_listener.stop()
        camera.release()
        print("Camera released")
        logging.info("Camera released")
        logging.info("Program stopped")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Fatal error: {e}")
        raise 