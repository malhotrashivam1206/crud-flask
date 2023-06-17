from flask import Flask, render_template, request, redirect, flash, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from wtforms import Form, StringField, TextAreaField
from wtforms.validators import InputRequired

app = Flask(__name__)
app.secret_key = 'secret_key'

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['notes_db']

# Define the NoteForm class
class NoteForm(Form):
    title = StringField('Title', validators=[InputRequired()])
    content = TextAreaField('Content', validators=[InputRequired()])

    def hidden_tag(self):
        return ''

# Routes
@app.route('/')
def get_notes():
    notes = db.notes.find()
    return render_template('index.html', notes=notes)

@app.route('/notes/create', methods=['GET', 'POST'])
def create_note():
    form = NoteForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        content = form.content.data
        db.notes.insert_one({'title': title, 'content': content})
        flash('Note created successfully', 'success')
        return redirect(url_for('get_notes'))
    return render_template('create_note.html', form=form)

@app.route('/notes/<note_id>/update', methods=['GET', 'POST'])
def update_note(note_id):
    note = db.notes.find_one({'_id': ObjectId(note_id)})
    form = NoteForm(request.form)

    if request.method == 'POST' and form.validate():
        updated_note = {
            'title': form.title.data,
            'content': form.content.data
        }
        db.notes.update_one({'_id': ObjectId(note_id)}, {'$set': updated_note})
        flash('Note updated successfully', 'success')
        return redirect(url_for('get_notes'))

    return render_template('update_note.html', form=form, note=note)

@app.route('/notes/<note_id>/delete', methods=['POST'])
def delete_note(note_id):
    db.notes.delete_one({'_id': ObjectId(note_id)})
    flash('Note deleted successfully', 'success')
    return redirect(url_for('get_notes'))

if __name__ == '__main__':
    app.run(debug=True)
