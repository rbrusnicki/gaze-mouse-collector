# Gaze, Mouse, and Keyboard Data Collector

A Python script that captures camera images along with mouse cursor and text caret positions when you interact with your computer.

## Setup

1. Install Python 3.7+ if you don't have it already.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:

```bash
python gaze_mouse_collector.py
```

2. The script captures data in two ways:
   - **Mouse clicks**: When you click anywhere on your screen, it captures an image and saves it with the cursor position.
   - **Keyboard input**: When you type, it captures an image and saves it with the text caret position (the blinking vertical line where text appears).

3. Press `Ctrl+C` in the terminal to stop the program.

## Output

The script creates two directories:

1. `mouse_data`: Contains images triggered by mouse clicks
   - Files are named: `TIMESTAMP_X_Y.jpg` where X and Y are the cursor coordinates when clicked

2. `keyboard_data`: Contains images triggered by keyboard input
   - Files are named: `TIMESTAMP_X_Y.jpg` where X and Y are the text caret coordinates (where the blinking text cursor is located)

In both cases, `TIMESTAMP` is the date and time of capture.

## Troubleshooting

- If the camera doesn't work, check that your USB camera is connected and recognized by your system.
- On Windows, you might need to run the script as administrator if you encounter permission issues.
- For keyboard monitoring, the script attempts to get the text caret position. If it can't determine the text caret position, it will skip capturing that key press.
- Text caret position detection works best in standard Windows applications (notepad, word processors, browsers, etc.)
- If you don't see keyboard captures happening, try typing in a different application where the text caret is more visible. 