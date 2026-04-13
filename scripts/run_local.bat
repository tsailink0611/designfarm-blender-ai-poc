@echo off
REM ===================================================
REM designfarm-blender-ai-poc 実行スクリプト (Windows)
REM ===================================================

SET PROJECT_ROOT=%~dp0..
SET PYTHONPATH=%PROJECT_ROOT%

REM Blenderのパスが未設定の場合はデフォルトを設定
IF "%BLENDER_PATH%"=="" (
    SET BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe
)

REM ルートA: 日本語指示からシーン生成
IF "%1"=="generate" (
    python "%PROJECT_ROOT%\src\app.py" generate "%~2" --output "%PROJECT_ROOT%\output"
    GOTO END
)

REM ルートB: 指定JSONからシーン生成
IF "%1"=="from-json" (
    python "%PROJECT_ROOT%\src\app.py" from-json "%~2"
    GOTO END
)

REM デフォルト: サンプルJSONで実行
echo サンプルJSONでシーン生成します...
python "%PROJECT_ROOT%\src\app.py" from-json "%PROJECT_ROOT%\samples\sample_layout_spec.json"

:END
