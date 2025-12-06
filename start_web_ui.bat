@echo off
echo ============================================
echo Starting Text-to-SQL Agent Web UI
echo ============================================
echo.

echo Installing dependencies...
C:\Users\HP\AppData\Local\Programs\Python\Python39\python.exe -m pip install -q streamlit plotly

echo.
echo Starting Streamlit server...
echo.
echo Web UI will open in your browser at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

C:\Users\HP\AppData\Local\Programs\Python\Python39\python.exe -m streamlit run web_ui.py
