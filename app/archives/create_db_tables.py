from clue import app, db

# Create an application context
with app.app_context():
    # Create the data tables
    db.create_all()
