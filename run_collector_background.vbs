Set WshShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
strPythonCmd = "pythonw.exe """ & strPath & "\gaze_mouse_collector.py"""
WshShell.Run strPythonCmd, 0, False 