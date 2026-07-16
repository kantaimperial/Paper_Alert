' Double-click launcher: runs start_paper_alert.bat with no visible console
' window. Must stay inside the paper-alert folder next to that file.
' (Kept ASCII-only: VBScript's legacy script host can mis-parse non-ASCII
' text depending on the system codepage, breaking string literals.)
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
batPath = scriptDir & "\start_paper_alert.bat"

If fso.FileExists(batPath) Then
    shell.CurrentDirectory = scriptDir
    shell.Run """" & batPath & """", 0, False
Else
    MsgBox "start_paper_alert.bat was not found." & vbCrLf & vbCrLf & _
           "Keep this file inside the paper-alert folder - moving or " & _
           "copying it out on its own will break it.", _
           vbExclamation, "Can't start paper-alert"
End If
