@echo off
echo ====================================
echo  BDIMS LaTeX Report Compilation
echo ====================================
echo.

echo [1/4] Running pdflatex (first pass)...
pdflatex -interaction=nonstopmode main.tex
if %errorlevel% neq 0 (
    echo Error in first pdflatex pass!
    pause
    exit /b 1
)

echo.
echo [2/4] Running biber for bibliography...
biber main
if %errorlevel% neq 0 (
    echo Warning: Biber encountered issues (this may be normal if no citations yet)
)

echo.
echo [3/4] Running pdflatex (second pass)...
pdflatex -interaction=nonstopmode main.tex
if %errorlevel% neq 0 (
    echo Error in second pdflatex pass!
    pause
    exit /b 1
)

echo.
echo [4/4] Running pdflatex (third pass for TOC)...
pdflatex -interaction=nonstopmode main.tex
if %errorlevel% neq 0 (
    echo Error in third pdflatex pass!
    pause
    exit /b 1
)

echo.
echo ====================================
echo  Compilation Complete!
echo ====================================
echo.
echo Output file: main.pdf
echo.
echo Cleaning up auxiliary files...
del /q *.aux *.log *.out *.toc *.lof *.lot *.bbl *.blg *.bcf *.run.xml 2>nul

echo.
echo Done! Opening PDF...
start main.pdf

pause
