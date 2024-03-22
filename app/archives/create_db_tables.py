from clue import app, db

# Create an application context
with app.app_context():
    # Create the database tables
    db.create_all()
