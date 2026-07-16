' Double-click launcher: runs start_paper_alert.bat with no visible console
' window. Must stay inside the paper-alert folder next to that file.
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
batPath = scriptDir & "\start_paper_alert.bat"

If fso.FileExists(batPath) Then
    shell.CurrentDirectory = scriptDir
    shell.Run """" & batPath & """", 0, False
Else
    MsgBox "start_paper_alert.bat が見つかりませんでした。" & vbCrLf & vbCrLf & _
           "このファイルは paper-alert フォルダの中に入れたまま使ってください。" & _
           "ファイル単体だけを別の場所に移動・コピーすると動かなくなります。", _
           vbExclamation, "paper-alertを起動できません"
End If
