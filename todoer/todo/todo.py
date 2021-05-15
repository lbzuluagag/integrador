from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort
from todo.auth import login_required
from todo.db import get_db
from .extensions import mongo
bp = Blueprint('todo', __name__)

@bp.route('/', methods=['GET','POST'])
def index():
    return render_template('todo/index.html')

@bp.route('/create', methods=['GET','POST'])
@login_required
def create():
    if request.method == "POST":
        description = request.form['description']
        error = None

        if not description:
            error = 'Description is required.'
        
        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute(
                'insert into todo (description, completed, created_by)'
                ' values (%s, %s, %s)',
                (description, False, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/create.html')

def get_todo(id):
    db, c = get_db()
    c.execute(
        'select t.id, t.description, t.completed, t.created_by, t.created_at, u.username '
        'from todo t JOIN users u on t.created_by = u.id where t.id = %s', (id,)
    )

    todo = c.fetchone()

    if todo is None:
        abort(404, f"This todo id {id} does not exist")
    return todo

@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    todo = get_todo(id)

    if request.method == "POST":
        description = request.form['description']
        completed = True if request.form.get('completed') == 'on' else False
        error = None
    
        if not description:
            error = 'Description is required'
        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute(
                "update todo set description = %s, completed = %s"
                " where id = %s",
                (description, completed, id)

            )

            db.commit()
            return redirect(url_for('todo.index'))
    return render_template('todo/update.html', todo=todo)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete():
    return ''



@bp.route('/horario', methods=['POST', 'GET'])
@login_required
def horario():
    horario=mongo.db.schedule.find_one()
    horario.pop("_id")
    return render_template('todo/horario.html', horario=horario)

@bp.route('/form', methods=['POST', 'GET'])
@login_required
def form():
    if request.method== "POST":
        print(request.form['esolar'])
        solar = request.form['esolar']
        eolica = request.form['eeolica']
        biomasa = request.form['ebiomasa']
        form_colletion = mongo.db.form
        form_colletion.delete_many({})
        form_colletion.insert_one({
            'solar': solar,
            'eolica': eolica,
            'biomasa': biomasa
        })
        #caputrar datos y supongo mandarlos a la base de datos
        #pendiente determinar tabla y campos para guardar eso
    return render_template('todo/form.html')

