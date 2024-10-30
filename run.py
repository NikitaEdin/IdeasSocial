from app import app
from create_db import create_database 

if __name__ == "__main__":
    # Always create the database when the app starts
    create_database()
    app.run(debug=True)
