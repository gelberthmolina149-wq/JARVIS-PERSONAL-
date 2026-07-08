@echo off
setlocal
set "ROOT=%~dp0"
pushd "%ROOT%"

set "PY314=C:\Users\User\AppData\Local\Programs\Python\Python314\python.exe"
set "MAIN=%ROOT%main.py"

if exist "%PY314%" (
    if exist "%MAIN%" (
        start "" /B "%PY314%" "%MAIN%"
        goto :done
    )
)

echo JARVIS: no se encontro Python 3.14 o main.py
pause
:done
popd
endlocal
