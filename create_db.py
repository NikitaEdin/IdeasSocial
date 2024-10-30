from app import app, db

def create_database():
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_database()
