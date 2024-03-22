import subprocess

subprocess.run(["export", "FLASK_APP=run.py"], shell=False)
subprocess.run(["flask", "run"])
