from app.models import User
from app import db, app

with app.app_context():
    user = User.query.filter_by(username='panda').first()
    print(user)
    db.session.delete(user)
    db.session.commit()
    print('User removed')