cwd = CreateObject("Scripting.FileSystemObject").GetFile(Wscript.ScriptFullName).ParentFolder.Path
path = cwd & "\cmd.bat"
Set shell = CreateObject("Shell.Application")
shell.ShellExecute path,"","","runas",0  ' 0代表不显示cmd命令窗口，1代表显示cmd命令行1窗口
WScript.Quit