import cv2
import os
import time
from datetime import datetime
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
import win32gui
import win32api

# Create directories for storing captured data
mouse_data_dir = "mouse_data"
keyboard_data_dir = "keyboard_data"
os.makedirs(mouse_data_dir, exist_ok=True)
os.makedirs(keyboard_data_dir, exist_ok=True)

# Initialize camera
camera = cv2.VideoCapture(0)  # 0 is typically the default camera

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
    Get the current text caret position
    """
    try:
        # Get the foreground window handle
        hwnd = win32gui.GetForegroundWindow()
        
        # Get the caret position
        caret_info = win32gui.GetGUIThreadInfo(win32api.GetWindowThreadProcessId(hwnd)[0])
        
        # Return the caret position
        if caret_info.rcCaret.left != 0 or caret_info.rcCaret.top != 0:
            return (caret_info.rcCaret.left, caret_info.rcCaret.top)
        else:
            # If caret position is not available, get the cursor position as a fallback
            return win32gui.GetCursorPos()
    except Exception as e:
        print(f"Error getting caret position: {e}")
        # Fallback to cursor position
        return win32gui.GetCursorPos()

def on_press(key):
    """
    Callback function that executes when a key is pressed
    """
    try:
        # Get current timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Get caret position
        x, y = get_caret_position()
        caret_position = (x, y)
        
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
                
            print(f"Key press captured at {timestamp} - Position: {caret_position} - Key: {char}")
        else:
            print("Failed to capture image from camera on key press")
    except Exception as e:
        print(f"Error in keyboard handler: {e}")

def main():
    print("Gaze, Mouse, and Keyboard Data Collector")
    print("----------------------------------------")
    print("Click anywhere to capture camera image and cursor position.")
    print("Type to capture camera image and caret position.")
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