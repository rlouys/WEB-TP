<strong>create venv :</strong><br>
python3 -m venv venv

<strong>activate venv : </strong><br>

win :<br> 
.\venv\Scripts\activate

linux:<br>
source venv/bin/activate<br>


<strong>Install requirements:</strong><br>
pip3 install -r requirements.txt

<strong>Run the app :</strong><br>
uvicorn app.main:app --reload
