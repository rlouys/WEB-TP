create venv :
python3 -m venv venv

activate venv : 

win : 
.\venv\Scripts\activate

linux:
source venv/bin/activate


Install requirements:
pip3 install -r requirements.txt

Run the app :
uvicorn app.main:app --reload
