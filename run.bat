@echo off
REM 設定編碼為 UTF-8 以支援中文顯示
chcp 65001 >nul

REM 虛擬環境名
set "venvDir=venv"

REM 尋找虛擬環境是否已存在 (檢查 activate.bat 是否存在)
if not exist "%venvDir%\Scripts\activate.bat" (
    echo Virtual environment not found, creating it for you...
    python -m venv "%venvDir%"
)

REM 開啟虛擬環境 (必須使用 call，否則會中斷目前腳本的執行)
echo Activating virtual environment...
call "%venvDir%\Scripts\activate.bat"

REM 安裝依賴項
if exist "requirements.txt" (
    echo 找到 requirements.txt 正在安裝依賴項...
    pip install -r requirements.txt
) else (
    echo 找不到 requirements.txt，將跳過安裝步驟。
)

REM 清空 console
cls

REM 啟動 PhotoServer.py
REM echo 正在執行 PhotoServer.py...
python PhotoServer.py

REM (可選) 讓視窗在結束後停留，方便查看錯誤訊息或執行結果。不需要可以刪除這行
pause