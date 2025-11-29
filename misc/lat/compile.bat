@echo off
echo ========================================
echo Compiling BDIMS Final Defense Report
echo ========================================
echo.

REM First compilation
echo [1/4] Running pdflatex (first pass)...
pdflatex -interaction=nonstopmode main.tex
if %ERRORLEVEL% NEQ 0 (
    echo Error in first pdflatex pass!
    pause
    exit /b %ERRORLEVEL%
)

REM Run biber for bibliography
echo.
echo [2/4] Processing bibliography with biber...
biber main
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Biber encountered issues, but continuing...
)

REM Second compilation
echo.
echo [3/4] Running pdflatex (second pass)...
pdflatex -interaction=nonstopmode main.tex
if %ERRORLEVEL% NEQ 0 (
    echo Error in second pdflatex pass!
    pause
    exit /b %ERRORLEVEL%
)

REM Third compilation for references
echo.
echo [4/4] Running pdflatex (final pass)...
pdflatex -interaction=nonstopmode main.tex
if %ERRORLEVEL% NEQ 0 (
    echo Error in final pdflatex pass!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================
echo SUCCESS! PDF generated: main.pdf
echo ========================================
echo.

REM Clean up auxiliary files (optional)
echo Cleaning up auxiliary files...
del main.aux main.log main.out main.toc main.lof main.lot main.bbl main.blg main.bcf main.run.xml 2>nul

echo.
echo Compilation complete! Check main.pdf
pause
