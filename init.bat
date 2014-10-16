@echo off
color 0b

rem mode con:cols=100 lines=42
rem 36*120
reg add "HKEY_CURRENT_USER\Console" /t REG_DWORD /v WindowSize /d 0x00240078 /f
rem 2000*120
reg add "HKEY_CURRENT_USER\Console" /t REG_DWORD /v ScreenBufferSize /d 0x07d00078 /f
reg add "HKEY_CURRENT_USER\Console" /t REG_DWORD /v QuickEdit /d 0x0000001 /f

rem color 08
python PasscarSender.py
