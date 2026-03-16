@echo off
echo ============================================
echo  BUILD - CEO Automacao WhatsApp Enterprise
echo ============================================

pip install pyinstaller --quiet

pyinstaller ^
  --onefile ^
  --windowed ^
  --name "CEO_WhatsApp" ^
  --icon NONE ^
  --hidden-import customtkinter ^
  --hidden-import pandas ^
  --hidden-import openpyxl ^
  --hidden-import selenium ^
  --hidden-import webdriver_manager ^
  --collect-all customtkinter ^
  main.py

echo.
echo ============================================
echo  Executavel gerado em: dist\CEO_WhatsApp.exe
echo ============================================
pause
