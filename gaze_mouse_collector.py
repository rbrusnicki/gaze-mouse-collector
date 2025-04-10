import cv2
import os
import time
from datetime import datetime
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
import win32gui
import win32api
from ctypes import windll, Structure, c_long, byref

# Create directories for storing captured data
mouse_data_dir = "mouse_data"
keyboard_data_dir = "keyboard_data"
os.makedirs(mouse_data_dir, exist_ok=True)
os.makedirs(keyboard_data_dir, exist_ok=True)

# Initialize camera
camera = cv2.VideoCapture(0)  # 0 is typically the default camera

# Define structure for getting caret position with more accuracy
class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

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
            
            print(f"Mouse click captured at {timestamp} - Position: {cursor_position}")
        else:
            print("Failed to capture image from camera")

def get_caret_position():
    """
    Get the current text caret position (the blinking vertical line where text appears)
    """
    try:
        # Get the foreground window handle
        hwnd = win32gui.GetForegroundWindow()
        
        # Get the GUI thread info for the foreground window
        thread_id = win32api.GetWindowThreadProcessId(hwnd)[0]
        caret_info = win32gui.GetGUIThreadInfo(thread_id)
        
        # Check if the caret position is valid (non-zero)
        if caret_info.rcCaret.left != 0 or caret_info.rcCaret.top != 0:
            # Return the center of the caret
            x = caret_info.rcCaret.left
            y = caret_info.rcCaret.top + (caret_info.rcCaret.bottom - caret_info.rcCaret.top) // 2
            return (x, y)
        
        # If the standard method doesn't work, try an alternative approach
        # Create a POINT structure for the caret
        caret_pos = POINT()
        
        # Try to get the caret position using alternative method
        if windll.user32.GetCaretPos(byref(caret_pos)):
            # Convert screen coordinates
            windll.user32.ClientToScreen(hwnd, byref(caret_pos))
            return (caret_pos.x, caret_pos.y)
            
        # If all methods fail, return None
        return None
    except Exception as e:
        print(f"Error getting caret position: {e}")
        return None

def on_press(key):
    """
    Callback function that executes when a key is pressed
    """
    try:
        # Get current timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Get caret position
        caret_position = get_caret_position()
        
        # Skip if we couldn't get the caret position
        if caret_position is None:
            print("Couldn't determine caret position, skipping capture")
            return
            
        x, y = caret_position
        
        # Capture image from camera
        ret, frame = camera.read()
        
        if ret:
            # Save the image with caret position in the filename
            image_path = os.path.join(keyboard_data_dir, f"{timestamp}_{x}_{y}.jpg")
            cv2.imwrite(image_path, frame)
            
            # Try to get the character typed
            char = ""
            try:
                char = str(key.char)
            except AttributeError:
                char = str(key)
                
            print(f"Key press captured at {timestamp} - Caret position: {caret_position} - Key: {char}")
        else:
            print("Failed to capture image from camera on key press")
    except Exception as e:
        print(f"Error in keyboard handler: {e}")

def main():
    print("Gaze, Mouse, and Keyboard Data Collector")
    print("----------------------------------------")
    print("Click anywhere to capture camera image and cursor position.")
    print("Type to capture camera image and text caret position (where text appears).")
    print("Press Ctrl+C in the terminal to stop the program.")
    
    # Start mouse and keyboard listeners
    mouse_listener = MouseListener(on_click=on_click)
    keyboard_listener = KeyboardListener(on_press=on_press)
    
    mouse_listener.start()
    keyboard_listener.start()
    
    try:
        # Keep the main thread alive
        while mouse_listener.is_alive() and keyboard_listener.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        # Stop listeners and release camera when program ends
        mouse_listener.stop()
        keyboard_listener.stop()
        camera.release()
        print("Camera released")

if __name__ == "__main__":
    main() 