from app import app, db
from app.models import User
from flask_migrate import Migrate, MigrateCommand
from flask_script import Shell, Manager

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User)

'''
@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
'''

# app
if __name__ == '__main__':
    app.run(debug=True)
    # manager.run()
