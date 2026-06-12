Set ws = CreateObject("WScript.Shell")
ws.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
ws.Run "cmd /c .venv\Scripts\activate.bat && python pygame_rockscissorpaper.py", 0, False
