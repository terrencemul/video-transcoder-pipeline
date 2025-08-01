@echo off
echo Video Transcoder Pipeline - Setup Test
echo =====================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Running setup validation...
python test_setup.py

echo.
pause
