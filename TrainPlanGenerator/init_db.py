import os
from app import db, app, User
from werkzeug.security import generate_password_hash

def init_app():

    basedir = os.path.abspath(os.path.dirname(__file__))
    db_folder = os.path.join(basedir, 'database')
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
        print(f"Created database directory at: {db_folder}")

   
    with app.app_context():
        
        db.create_all()
        print("Created all database tables")

      
        if not User.query.filter_by(username='test').first():
            test_user = User(
                username='test',
                email='test@example.com',
                password_hash=generate_password_hash('test123'),
                usage_count=0  # Initialize usage count to zero
            )
            db.session.add(test_user)
            db.session.commit()
            print("Created test user:")
            print("Username: test")
            print("Password: test123")

if __name__ == '__main__':
    init_app()
    print("Initialization complete!")
