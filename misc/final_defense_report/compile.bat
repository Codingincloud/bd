@echo off
echo ========================================
echo BDIMS Final Defense Report Compilation
echo ========================================
echo.

cd /d "%~dp0"

echo Checking for pdflatex...
where pdflatex >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: pdflatex not found!
    echo.
    echo Please install MiKTeX from: https://miktex.org/download
    echo.
    echo Or use Overleaf: https://www.overleaf.com/
    echo See COMPILE_INSTRUCTIONS.md for details
    echo.
    pause
    exit /b 1
)

echo Found pdflatex!
echo.
echo Compiling main_compilable.tex...
echo.

echo [1/4] First pdflatex pass...
pdflatex -interaction=nonstopmode main_compilable.tex
if %ERRORLEVEL% NEQ 0 (
    echo ERROR during first compilation pass!
    pause
    exit /b 1
)

echo [2/4] Running biber for bibliography...
biber main_compilable
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: biber failed, continuing anyway...
)

echo [3/4] Second pdflatex pass...
pdflatex -interaction=nonstopmode main_compilable.tex

echo [4/4] Final pdflatex pass...
pdflatex -interaction=nonstopmode main_compilable.tex

echo.
echo ========================================
echo Compilation complete!
echo ========================================
echo.
echo PDF file: main_compilable.pdf
echo.

if exist main_compilable.pdf (
    echo Opening PDF...
    start main_compilable.pdf
) else (
    echo ERROR: PDF was not created!
    echo Check main_compilable.log for errors
)

echo.
pause
