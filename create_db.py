import os
import secrets
from dotenv import load_dotenv
from app import app, db

env_path = '.env'

# Auto generate .ENV file with secret_key
if not os.path.exists(env_path):
    with open(env_path, 'w') as env_file:
        secret_key = secrets.token_hex(16)
        env_file.write(f"SECRET_KEY={secret_key}\n")  
        env_file.write(f"DATABASE_URL=sqlite:///site.db\n") 
    print('New .env file created with generated SECRET_KEY')

# Load environment variables
load_dotenv(env_path)


def create_database():
    with app.app_context():
        try:
            db.create_all()
            print(f"Database created successfully.")
        except Exception as e:
            print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_database()
