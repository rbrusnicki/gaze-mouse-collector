# Gaze Mouse Collector

## Purpose

This script is designed to collect data while you normally use your computer. It captures:
- Camera images (showing your face)
- Cursor positions when you click your mouse
- Text caret positions when you type

The collected dataset will be used to train a "Gaze Detector" - a machine learning model that can infer where on the screen you are looking based solely on camera images of your face. This enables the development of eye-tracking systems without specialized hardware.

By running this collector in the background during your regular computer use, you accumulate a rich dataset that maps your facial appearance to specific screen coordinates where your attention is focused.

## Setup

1. Install Python 3.7+ if you don't have it already.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running Manually

1. Run the script:

```bash
python gaze_mouse_collector.py
```

2. The script captures data in two ways:
   - **Mouse clicks**: When you click anywhere on your screen, it captures an image and saves it with the cursor position.
   - **Keyboard input**: When you type, it captures an image and saves it with the text caret position (the blinking vertical line where text appears).

3. Press `Ctrl+C` in the terminal to stop the program.

### Setting Up Auto-Start (Run in Background)

#### Method 1: Using Windows Startup Folder (Recommended)

1. Press `Win+R` to open the Run dialog
2. Type `shell:startup` and press Enter (this opens your Windows Startup folder)
3. Copy the `run_collector_background.vbs` file from this folder to the Startup folder
    - Alternatively, right-click in the Startup folder, select "New" → "Shortcut"
    - Enter the full path to the VBS file and click Next, then Finish

#### Method 2: Using Task Scheduler

1. Press `Win+R`, type `taskschd.msc` and press Enter to open Task Scheduler
2. Click "Create Basic Task" in the right panel
3. Enter a name (e.g., "Gaze Mouse Collector") and click Next
4. Select "When I log on" and click Next
5. Select "Start a program" and click Next
6. Browse to select `run_collector_background.vbs` and click Next
7. Check "Open the Properties dialog..." and click Finish
8. In the Properties dialog, go to the Conditions tab
9. Uncheck "Start the task only if the computer is on AC power"
10. Click OK to save

#### Verifying It's Running in the Background

After setting up:

1. Restart your computer or log out and log in again
2. Check the log folder for a new log file with today's date
3. The program is working if new images appear in the mouse_data or keyboard_data folders when you interact with your computer

#### Stopping the Background Program

If you need to stop the program:

1. Press `Ctrl+Shift+Esc` to open Task Manager
2. Look for "Python" or "pythonw.exe" processes in the list
3. Select it and click "End task"

## Output

The script creates two directories:

1. `mouse_data`: Contains images triggered by mouse clicks
   - Files are named: `TIMESTAMP_X_Y.jpg` where X and Y are the cursor coordinates when clicked

2. `keyboard_data`: Contains images triggered by keyboard input
   - Files are named: `TIMESTAMP_X_Y.jpg` where X and Y are the text caret coordinates (where the blinking text cursor is located)

In both cases, `TIMESTAMP` is the date and time of capture.

The script also creates a `log` folder with log files that record all activity.

## Troubleshooting

- If the camera doesn't work, check that your USB camera is connected and recognized by your system.
- On Windows, you might need to run the script as administrator if you encounter permission issues.
- For keyboard monitoring, the script attempts to get the text caret position. If it can't determine the text caret position, it will skip capturing that key press.
- Text caret position detection works best in standard Windows applications (notepad, word processors, browsers, etc.)
- If you don't see keyboard captures happening, try typing in a different application where the text caret is more visible.
- If the program isn't starting automatically, try running `run_collector_background.vbs` directly by double-clicking it
- Check the log folder for any error messages if you're having issues
- Ensure the Python environment has all the required packages 