@echo off
echo Running Python backend > run_output.log
python -m venv venv >> run_output.log 2>&1
call venv\Scripts\activate.bat >> run_output.log 2>&1
pip install -r requirements.txt >> run_output.log 2>&1
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 >> run_output.log 2>&1
