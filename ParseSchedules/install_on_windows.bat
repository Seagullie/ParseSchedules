rem create a virtual environment
python -m venv ../ParseSchedules
rem activate the virtual environment
call ./Scripts/activate
rem install the required packages
pip install -r requirements.txt
echo "Virtual environment created and packages installed"
