import os
from flask import Flask, request, url_for, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, instance_relative_config=True)

# # Determine the correct database path based on the environment
# if os.getenv("VERCEL_ENV"):
#     # If the app is running on Vercel, store the database in the writable /tmp directory
#     db_path = '/tmp/test.db'
# else:
#     # If running locally, store the database in the instance directory
#     db_path = os.path.join(app.instance_path, 'test.db')

# Simulate Vercel environment locally
os.environ["VERCEL_ENV"] = "development"

# Set the database path
db_path = '/tmp/test.db' if os.getenv("VERCEL_ENV") else os.path.join(os.getcwd(), 'instance', 'test.db')


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional: Disable track modifications

db = SQLAlchemy(app)

# Create the instance folder if it doesn't exist
os.makedirs(app.instance_path, exist_ok=True)

# Ensure the database and tables are created
with app.app_context():
    db.create_all()  # Create the tables if they don't exist

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('index', _external=True))

        except Exception as e:
            print(f"Error adding task: {str(e)}")  # Print the error for debugging
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try: 
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for('index', _external=True))
    
    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        print(f"Error deleting task: {str(e)}")
        return "There was a problem"

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect(url_for('index', _external=True))

        except Exception as e:
            db.session.rollback()
            print(f"Error updating task: {str(e)}")
            return 'There was a problem'

    else:
        return render_template('update.html', task=task)

if __name__ == "__main__":
    app.run(debug=True)
