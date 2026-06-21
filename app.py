from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super secret key"
DB ="notes.db"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notes (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 title TEXT NOT NULL,
                 content TEXT,
                 date_created TEXT
            )
    ''')
    conn.commit()
    conn.close()
#----------------------------

@app.route('/notes')
def notes_list():
    conn = get_db()
    notes = conn.execute('''SELECT * FROM notes ORDER BY id DESC''').fetchall()
    conn.close()
    return render_template('notes_list.html', notes=notes)

@app.route('/notes/<int:id>')
def note_detail(id):
    conn = get_db()
    note = conn.execute('''SELECT * FROM notes WHERE id = ?''', (id, )).fetchone()
    conn.close()
    if note is None:
        return "note not found", 404
    return render_template('notes_detail.html', note=note)

@app.route('/notes/new', methods=['GET', 'POST'])
def note_new():
    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        date_created = request.form.get('date_created', '')

        if not date_created:
            date_created = str(datetime.now().strftime("%Y-%m-%d %H:%M"))


        if not title or not content:
            flash("please fill the form")
            return redirect(url_for('note_new'))

        conn = get_db()
        conn.execute('''
            INSERT INTO notes (title, content, date_created) VALUES (?, ?, ?)''', (title, content, date_created)
        )
        conn.commit()
        conn.close()

        flash("Congratulations, note added")
        return redirect(url_for('notes_list'))

    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
    return render_template('note_form.html', note=None, current_time=current_time)



@app.route('/notes/<int:id>/edit', methods=['GET', 'POST'])
def note_edit(id):
    conn = get_db()
    note = conn.execute('''SELECT * FROM notes WHERE id = ?''', (id,)).fetchone()

    if note is None:
        conn.close()
        return "Note not found", 404

    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        date_created = request.form.get('date_created', '')

        if not title or not content:
            flash("please fill the form")
            conn.close()
            return redirect(url_for('note_edit', id=id))

        conn.execute('''
            UPDATE notes SET title = ?, content = ?, date_created = ? WHERE id = ?
        ''', (title, content, date_created, id))

        conn.commit()
        conn.close()

        return redirect(url_for('note_detail', id=id))

    conn.close()
    return render_template('note_form.html', note=note)

@app.route('/notes/<int:id>/delete', methods=['GET', 'POST'])
def note_delete(id):
    conn = get_db()
    conn.execute('''
        DELETE FROM notes WHERE id = ?
    ''', (id,))
    conn.commit()
    conn.close()

    flash("Note deleted!")
    return redirect(url_for('notes_list'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)