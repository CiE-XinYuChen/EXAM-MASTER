"""EXAM-MASTER: a small, server-rendered question bank and study app."""
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, Response, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from db import (FIELDS, LETTERS, TYPES, UPSERT, close_db, export_csv, get_db, grade,
                import_csv, init_db, parse_question, query, question, unpack)

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY', 'exam-master-local'),
                  DATABASE=os.environ.get('EXAM_DATABASE', str(ROOT / 'database.db')),
                  SEED_CSV=os.environ.get('EXAM_SEED_CSV', str(ROOT / 'questions.csv')),
                  PERMANENT_SESSION_LIFETIME=timedelta(days=7))
app.teardown_appcontext(close_db)
with app.app_context():
    init_db()


@app.before_request
def current_user():
    g.user = query('SELECT * FROM users WHERE id=?', (session.get('user_id'),), one=True)
    if request.endpoint and request.endpoint not in ('login', 'register', 'static') and not g.user:
        return redirect(url_for('login'))


@app.context_processor
def shared_context():
    counts = {row['qtype']: row['n'] for row in query('SELECT qtype,COUNT(*) AS n FROM questions GROUP BY qtype')}
    return dict(types=TYPES, letters=LETTERS, today=datetime.now().strftime('%Y年%m月%d日'),
                type_counts={key: counts[key] for key in TYPES if key in counts}, bank_total=sum(counts.values()))


@app.route('/login', methods=['GET', 'POST'], endpoint='login')
@app.route('/register', methods=['GET', 'POST'], endpoint='register')
def auth():
    register = request.endpoint == 'register'
    error = None
    if request.method == 'POST':
        name, password = request.form.get('username', '').strip(), request.form.get('password', '')
        user = query('SELECT * FROM users WHERE username=?', (name,), one=True)
        if not name or not password:
            error = '请填写用户名和密码。'
        elif register:
            if user:
                error = '这个用户名已被使用。'
            elif len(password) < 6 or password != request.form.get('confirm_password'):
                error = '密码至少 6 位，两次输入需要一致。'
            else:
                with get_db() as conn:
                    conn.execute('INSERT INTO users (username,password_hash) VALUES (?,?)',
                                 (name, generate_password_hash(password)))
                flash('账号已创建，请登录。', 'success')
                return redirect(url_for('login'))
        elif user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session.permanent = True
            return redirect(url_for('index'))
        else:
            error = '用户名或密码不正确。'
    return render_template('auth.html', register=register, error=error), 400 if error else 200


@app.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


def filters(scope='all'):
    values = {key: request.values.get(key, '').strip() for key in ('search', 'type', 'category', 'difficulty')}
    values['search'] = values['search'] or request.values.get('query', '').strip()
    clauses, params = [], []
    if values['search']:
        clauses.append('(q.stem LIKE ? OR q.id LIKE ?)')
        params += ['%' + values['search'] + '%'] * 2
    for key, column in [('type', 'qtype'), ('category', 'category'), ('difficulty', 'difficulty')]:
        if values[key] and values[key] != 'all':
            clauses.append(f'q.{column}=?')
            params.append(values[key])
    if scope in ('favorites', 'wrong'):
        table = 'favorites' if scope == 'favorites' else 'history'
        clauses.append(f'EXISTS (SELECT 1 FROM {table} h WHERE h.question_id=q.id AND h.user_id=?'
                       + (' AND h.correct=0)' if scope == 'wrong' else ')'))
        params.append(g.user['id'])
    return values, (' WHERE ' + ' AND '.join(clauses) if clauses else ''), params


def choices():
    return {key: [row['value'] for row in query(f'SELECT DISTINCT {key} AS value FROM questions '
                                               f'WHERE {key} IS NOT NULL AND {key}!="" ORDER BY {key}')]
            for key in ('category', 'difficulty')}


def question_list(scope='all'):
    values, where, params = filters(scope)
    total = query('SELECT COUNT(*) AS n FROM questions q' + where, params, one=True)['n']
    pages = max(1, (total + 19) // 20)
    page = min(max(1, request.args.get('page', 1, type=int)), pages)
    rows = query('SELECT q.*, f.tag, f.id IS NOT NULL AS favorite FROM questions q '
                 'LEFT JOIN favorites f ON f.question_id=q.id AND f.user_id=?' + where +
                 ' ORDER BY CAST(q.id AS INTEGER), q.id LIMIT 20 OFFSET ?',
                 [g.user['id'], *params, (page - 1) * 20])
    return render_template('questions.html', questions=[unpack(row) for row in rows], scope=scope,
                           total=total, page=page, pages=pages, filters=values, choices=choices(),
                           incomplete=total - len(practice_ids(scope)))


@app.get('/questions')
def questions():
    return question_list()


@app.get('/favorites')
def favorites():
    return question_list('favorites')


@app.get('/wrong')
def wrong():
    return question_list('wrong')


@app.route('/questions/new', methods=['GET', 'POST'])
@app.route('/questions/<path:qid>/edit', methods=['GET', 'POST'])
def edit_question(qid=None):
    used_ids = {row['id'] for row in query('SELECT id FROM questions UNION SELECT question_id FROM history '
                                         'UNION SELECT value FROM exam_sessions,json_each(question_ids)')} if not qid else set()
    row = question(qid) if qid else dict(id=str(max((int(value) for value in used_ids if value.isdecimal()), default=0) + 1),
                                       stem='', answer='', options={}, qtype=TYPES[0],
                                       category='', difficulty='无', explanation='')
    if row is None:
        abort(404)
    error = None
    if request.method == 'POST':
        try:
            data = parse_question(dict(request.form) | ({'id': qid} if qid else {}))
            if not qid and data['id'] in used_ids:
                raise ValueError('这个题号已用于题目或学习记录，请使用新题号；修改已有题目请使用编辑。')
            with get_db() as conn:
                conn.execute(UPSERT, tuple(data[key] for key in FIELDS))
            flash('题目已保存。', 'success')
            return redirect(url_for('questions'))
        except ValueError as exc:
            error = str(exc)
            row = dict(request.form) | {'id': qid or request.form.get('id', ''),
                                       'options': {key: request.form.get(key, '') for key in LETTERS}}
    return render_template('edit.html', question=row, editing=bool(qid), error=error, choices=choices()), 400 if error else 200


@app.post('/questions/<path:qid>/delete')
def delete_question(qid):
    with get_db() as conn:
        conn.execute('DELETE FROM questions WHERE id=?', (qid,))
        conn.execute('DELETE FROM favorites WHERE question_id=?', (qid,))
        conn.execute('UPDATE users SET current_seq_qid=NULL WHERE current_seq_qid=?', (qid,))
    flash('题目已删除，已有答题记录仍保留。', 'success')
    return redirect(url_for('questions'))


@app.route('/questions/import', methods=['GET', 'POST'])
def import_questions():
    error = None
    if request.method == 'POST':
        try:
            upload = request.files.get('file')
            if not upload or not upload.filename:
                raise ValueError('请选择 CSV 文件。')
            added, updated = import_csv(upload.read().decode('utf-8-sig'))
            flash(f'导入完成：新增 {added} 题，更新 {updated} 题。', 'success')
            return redirect(url_for('questions'))
        except (ValueError, UnicodeError) as exc:
            error = '请使用 UTF-8 编码的 CSV 文件。' if isinstance(exc, UnicodeError) else str(exc)
    return render_template('import.html', error=error), 400 if error else 200


@app.get('/questions/export')
def export_questions():
    if request.args.get('template'):
        return Response(export_csv([]), mimetype='text/csv',
                        headers={'Content-Disposition': 'attachment; filename=question-template.csv'})
    _, where, params = filters(request.args.get('scope', 'all'))
    rows = query('SELECT q.* FROM questions q' + where + ' ORDER BY CAST(q.id AS INTEGER),q.id', params)
    return Response(export_csv(rows), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=questions.csv'})


@app.get('/', endpoint='index')
@app.get('/statistics', endpoint='statistics')
def index():
    uid = g.user['id']
    stats = query('SELECT COUNT(*) AS attempts, COALESCE(SUM(correct),0) AS correct FROM history WHERE user_id=?',
                  (uid,), one=True)
    stats['total'] = query('SELECT COUNT(*) AS n FROM questions', one=True)['n']
    stats['answered'] = query('SELECT COUNT(DISTINCT h.question_id) AS n FROM history h '
                             'JOIN questions q ON q.id=h.question_id WHERE h.user_id=?', (uid,), one=True)['n']
    stats['accuracy'] = round(100 * stats['correct'] / stats['attempts']) if stats['attempts'] else 0
    stats['progress'] = round(100 * stats['answered'] / stats['total']) if stats['total'] else 0
    stats['wrong'] = query('SELECT COUNT(DISTINCT h.question_id) AS n FROM history h JOIN questions q '
                          'ON q.id=h.question_id WHERE h.user_id=? AND h.correct=0', (uid,), one=True)['n']
    groups = {}
    for field in ('category', 'difficulty'):
        groups[field] = query(f'SELECT COALESCE(NULLIF(q.{field},""),"未分类") AS name, '
                               'COUNT(*) AS n, ROUND(AVG(h.correct)*100) AS accuracy FROM history h '
                               f'JOIN questions q ON h.question_id=q.id WHERE h.user_id=? GROUP BY q.{field}', (uid,))
    recent = query('SELECT * FROM exam_sessions WHERE user_id=? AND completed=1 ORDER BY id DESC LIMIT 5', (uid,))
    worst = query('SELECT q.id,q.stem,COUNT(*) AS n FROM history h JOIN questions q ON q.id=h.question_id '
                  'WHERE h.user_id=? AND h.correct=0 GROUP BY q.id ORDER BY n DESC LIMIT 5', (uid,))
    return render_template('dashboard.html', stats=stats, groups=groups, recent=recent, worst=worst)


@app.get('/history')
def history():
    total = query('SELECT COUNT(*) AS n FROM history WHERE user_id=?', (g.user['id'],), one=True)['n']
    pages = max(1, (total + 19) // 20)
    page = min(max(1, request.args.get('page', 1, type=int)), pages)
    rows = query('SELECT h.*,q.stem,datetime(h.timestamp,"localtime") AS display_time FROM history h '
                 'LEFT JOIN questions q ON q.id=h.question_id WHERE h.user_id=? ORDER BY h.id DESC LIMIT 20 OFFSET ?',
                 (g.user['id'], (page - 1) * 20))
    return render_template('history.html', history=rows, total=total, page=page, pages=pages)


@app.post('/reset_history')
def reset_history():
    with get_db() as conn:
        conn.execute('DELETE FROM history WHERE user_id=?', (g.user['id'],))
        conn.execute('UPDATE users SET current_seq_qid=NULL WHERE id=?', (g.user['id'],))
    flash('答题历史与顺序进度已重置。', 'success')
    return redirect(url_for('index'))


def practice_ids(mode):
    _, where, params = filters(mode if mode in ('wrong', 'favorites') else 'all')
    return [row['id'] for row in query('SELECT q.* FROM questions q' + where +
                                      ' ORDER BY CAST(q.id AS INTEGER),q.id', params) if not unpack(row)['issue']]


@app.get('/practice/<mode>')
def practice(mode):
    if mode not in ('random', 'sequential', 'wrong', 'favorites'):
        abort(404)
    ids = practice_ids(mode)
    answered = {row['question_id'] for row in query('SELECT DISTINCT question_id FROM history WHERE user_id=?', (g.user['id'],))}
    remaining = [qid for qid in ids if qid not in answered] if mode in ('random', 'sequential') else ids
    if mode == 'sequential':
        saved = g.user['current_seq_qid']
        qid = saved if saved in ids else next(iter(remaining or ids), None)
    else:
        qid = random.choice(remaining) if remaining else None
    if not qid:
        return render_template('question.html', question=None, mode=mode)
    return redirect(url_for('show_question', qid=qid, **(dict(request.args) | {'mode': mode})))


@app.route('/question/<path:qid>', methods=['GET', 'POST'])
def show_question(qid, mode=None):
    mode = mode or request.args.get('mode', 'single')
    row = question(qid)
    if row is None:
        abort(404)
    uid = g.user['id']
    ids = practice_ids(mode)
    values, _, _ = filters()
    practice_filters = {key: value for key, value in values.items() if value}
    answered = {item['question_id'] for item in query('SELECT DISTINCT question_id FROM history WHERE user_id=?', (uid,))}
    result = query('SELECT * FROM history WHERE id=? AND user_id=? AND question_id=?',
                   (request.args.get('attempt'), uid, qid), one=True)
    start = ids.index(qid) + 1 if qid in ids else 0
    following = ids[start:] + ids[:start]
    next_id = next((item for item in following if item not in answered | {qid}), next(iter(following), None))
    if request.method == 'POST':
        if row['issue']:
            flash('请先在题库管理中补全这道题。', 'error')
            return redirect(url_for('edit_question', qid=qid))
        answer, correct = grade(row, request.form.getlist('answer'))
        if not answer:
            flash('请先填写或选择答案。', 'error')
            return redirect(url_for('show_question', qid=qid, mode=mode, **practice_filters))
        with get_db() as conn:
            attempt = conn.execute('INSERT INTO history (user_id,question_id,user_answer,correct) VALUES (?,?,?,?)',
                                   (uid, qid, answer, correct)).lastrowid
            if mode == 'sequential':
                conn.execute('UPDATE users SET current_seq_qid=? WHERE id=?', (next_id, uid))
        return redirect(url_for('show_question', qid=qid, mode=mode, attempt=attempt, **practice_filters))
    if mode == 'sequential' and not result:
        with get_db() as conn:
            conn.execute('UPDATE users SET current_seq_qid=? WHERE id=?', (qid, uid))
    favorite = query('SELECT * FROM favorites WHERE user_id=? AND question_id=?', (uid, qid), one=True)
    next_url = url_for('show_question', qid=next_id, mode=mode, **practice_filters) if mode == 'sequential' and next_id else url_for('practice', mode=mode if mode != 'single' else 'random', **practice_filters)
    return render_template('question.html', question=row, mode=mode, result=result, favorite=favorite,
                           next_url=next_url, position=ids.index(qid) + 1 if qid in ids else 1,
                           total=len(ids), answered=len(set(ids) & answered), practice_filters=practice_filters)


@app.route('/sequential/<path:qid>', methods=['GET', 'POST'])
def sequential_question(qid):
    return show_question(qid, 'sequential')


@app.post('/favorite/<path:qid>', endpoint='favorite')
@app.post('/unfavorite/<path:qid>', endpoint='unfavorite')
@app.post('/update_tag/<path:qid>', endpoint='update_tag')
def bookmark(qid):
    if question(qid) is None:
        abort(404)
    with get_db() as conn:
        if request.endpoint == 'unfavorite':
            conn.execute('DELETE FROM favorites WHERE user_id=? AND question_id=?', (g.user['id'], qid))
        else:
            conn.execute('INSERT INTO favorites (user_id,question_id,tag) VALUES (?,?,?) '
                         'ON CONFLICT(user_id,question_id) DO UPDATE SET tag=excluded.tag',
                         (g.user['id'], qid, request.form.get('tag', '')))
    return redirect(request.form.get('next') or url_for('show_question', qid=qid))


@app.get('/modes')
def modes():
    return render_template('modes.html', total=query('SELECT COUNT(*) AS n FROM questions', one=True)['n'], choices=choices())


@app.post('/start_exam', endpoint='start_exam')
@app.post('/start_timed_mode', endpoint='start_timed_mode')
def start_exam():
    timed = request.endpoint == 'start_timed_mode' or request.form.get('mode') == 'timed'
    count = request.form.get('question_count', 10, type=int)
    minutes = request.form.get('duration', 10, type=int) if timed else 0
    if count < 1 or (timed and minutes < 1):
        flash('题量和限时需要大于 0。', 'error')
        return redirect(url_for('modes'))
    _, where, params = filters()
    available = [unpack(row) for row in query('SELECT q.* FROM questions q' + where, params) if not unpack(row)['issue']]
    paper = random.sample(available, min(count, len(available)))
    if not paper:
        flash('当前条件下没有题目，请先添加题目或调整筛选。', 'error')
        return redirect(url_for('modes'))
    with get_db() as conn:
        exam_id = conn.execute('INSERT INTO exam_sessions (user_id,mode,question_ids,start_time,duration,paper) VALUES (?,?,?,?,?,?)',
                              (g.user['id'], 'timed' if timed else 'exam', json.dumps([q['id'] for q in paper]),
                               datetime.now().isoformat(timespec='seconds'), minutes * 60,
                               json.dumps(paper, ensure_ascii=False))).lastrowid
    session['current_exam_id'] = exam_id
    return redirect(url_for('exam', exam_id=exam_id))


@app.route('/exam/<int:exam_id>', methods=['GET', 'POST'])
def exam(exam_id):
    record = query('SELECT * FROM exam_sessions WHERE id=? AND user_id=?', (exam_id, g.user['id']), one=True)
    if record is None:
        abort(404)
    paper = json.loads(record['paper'] or '[]')
    legacy = not paper and record['completed']
    if not paper and not record['completed']:
        paper = [row for qid in json.loads(record['question_ids']) if (row := question(qid))]
    if request.method == 'POST' and not record['completed']:
        for row in paper:
            row['user_answer'], row['correct'] = grade(row, request.form.getlist('answer_' + row['id']))
        score = round(100 * sum(row['correct'] for row in paper) / len(paper), 1) if paper else 0
        with get_db() as conn:
            changed = conn.execute('UPDATE exam_sessions SET completed=1,score=?,paper=? WHERE id=? AND completed=0',
                                   (score, json.dumps(paper, ensure_ascii=False), exam_id)).rowcount
            if changed:
                conn.executemany('INSERT INTO history (user_id,question_id,user_answer,correct) VALUES (?,?,?,?)',
                                 [(g.user['id'], row['id'], row['user_answer'], row['correct']) for row in paper])
        if session.get('current_exam_id') == exam_id:
            session.pop('current_exam_id', None)
        return redirect(url_for('exam', exam_id=exam_id))
    deadline = (datetime.fromisoformat(record['start_time']) + timedelta(seconds=record['duration'])).timestamp() * 1000 if record['duration'] else 0
    return render_template('exam.html', exam=record, questions=paper, deadline=deadline, legacy=legacy)


@app.route('/exam', methods=['GET'])
@app.route('/timed_mode', methods=['GET'])
@app.route('/submit_exam', methods=['POST'])
@app.route('/submit_timed_mode', methods=['GET', 'POST'])
def current_exam():
    exam_id = session.get('current_exam_id')
    if exam_id and request.method == 'POST':
        return exam(exam_id)
    return redirect(url_for('exam', exam_id=exam_id) if exam_id else url_for('modes'))


@app.route('/browse')
@app.route('/search', methods=['GET', 'POST'])
@app.route('/filter', methods=['GET', 'POST'])
def old_list():
    return redirect(url_for('questions', **request.values))


@app.get('/random')
@app.get('/sequential_start')
@app.get('/only_wrong')
def old_practice():
    return practice({'/random': 'random', '/sequential_start': 'sequential', '/only_wrong': 'wrong'}[request.path])


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 32220)), debug=os.environ.get('FLASK_DEBUG') == '1')
