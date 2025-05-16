import csv
import sqlite3
import random
import json
import time
from datetime import datetime, timedelta
from flask import Flask, request, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash


app = Flask(__name__)
app.secret_key = 'yoursecretkey'  # 请使用安全随机密钥

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # 用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT
    )''')
    try:
        c.execute('ALTER TABLE users ADD COLUMN current_seq_qid TEXT')
    except sqlite3.OperationalError:
        # 列已存在就什么都不做
        pass

    # 答题历史表
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question_id TEXT,
        user_answer TEXT,
        correct INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # 题目表（将题库入库）
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
        id TEXT PRIMARY KEY,
        stem TEXT,
        answer TEXT,
        difficulty TEXT,
        qtype TEXT,
        category TEXT,
        options TEXT -- JSON存储选项，例如{"A":"选项A", "B":"选项B"...}
    )''')
    # 收藏表
    c.execute('''CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question_id TEXT,
        tag TEXT,
        UNIQUE(user_id, question_id)
    )''')
    # 模拟考试与定时模式会话表（示例用途）
    c.execute('''CREATE TABLE IF NOT EXISTS exam_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        mode TEXT, -- exam或timed
        question_ids TEXT, -- JSON列表
        start_time DATETIME,
        duration INTEGER -- 以秒为单位，例如600秒=10分钟
    )''')
    conn.commit()

    # 如果questions表为空，则从CSV导入
    c.execute('SELECT COUNT(*) as cnt FROM questions')
    if c.fetchone()['cnt'] == 0:
        load_questions_to_db(conn)

    conn.close()

def load_questions_to_db(conn):
    with open('questions.csv','r',encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        c = conn.cursor()
        for row in reader:
            options = {}
            for opt in ['A','B','C','D','E']:
                if row.get(opt) and row[opt].strip():
                    options[opt] = row[opt]
            c.execute(
                "INSERT INTO questions (id, stem, answer, difficulty, qtype, category, options) VALUES (?,?,?,?,?,?,?)",
                (
                    row["题号"],
                    row["题干"],
                    row["答案"],
                    row["难度"],
                    row["题型"],
                    row.get("类别", "未分类"),
                    json.dumps(options, ensure_ascii=False),
                ),
            )
        conn.commit()

init_db()

def is_logged_in():
    return 'user_id' in session

def get_user_id():
    return session.get('user_id')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            conn = get_db()
            c = conn.cursor()
            c.execute('SELECT id FROM users WHERE username=?', (username,))
            if c.fetchone():
                return "用户名已存在，请更换用户名"
            password_hash = generate_password_hash(password)
            c.execute('INSERT INTO users (username,password_hash) VALUES (?,?)', (username,password_hash))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT id, password_hash FROM users WHERE username=?', (username,))
        user = c.fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        else:
            return "登录失败，用户名或密码错误"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('index.html')

def fetch_question(qid):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM questions WHERE id=?',(qid,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row['id'],
            'stem': row['stem'],
            'answer': row['answer'],
            'difficulty': row['difficulty'],
            'type': row['qtype'],
            'category': row['category'],
            'options': json.loads(row['options'])
        }
    return None

def random_question_id(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT id FROM questions 
        WHERE id NOT IN (
            SELECT question_id FROM history WHERE user_id=?
        )
        ORDER BY RANDOM() 
        LIMIT 1
    ''', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return row['id']
    return None


@app.route('/reset_history', methods=['POST'])
def reset_history():
    if not is_logged_in():
        return redirect(url_for('login'))
    user_id = get_user_id()
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM history WHERE user_id=?', (user_id,))
    conn.commit()
    conn.close()
    flash("答题历史已重置。现在您可以重新开始答题。")
    return redirect(url_for('random_question'))

@app.route('/random', methods=['GET'])
def random_question():
    if not is_logged_in():
        return redirect(url_for('login'))
    user_id = get_user_id()
    qid = random_question_id(user_id)
    conn = get_db()
    c = conn.cursor()
    # 获取总题数
    c.execute('SELECT COUNT(*) as total FROM questions')
    total = c.fetchone()['total']
    # 获取已答题数
    c.execute('SELECT COUNT(*) as answered FROM history WHERE user_id=?', (user_id,))
    answered = c.fetchone()['answered']
    conn.close()
    
    if not qid:
        # 传递 question=None 以及进度数据
        return render_template('question.html', question=None, answered=answered, total=total)
    q = fetch_question(qid)
    return render_template('question.html', question=q, answered=answered, total=total)


@app.route('/question/<qid>', methods=['GET','POST'])
def show_question(qid):
    if not is_logged_in():
        return redirect(url_for('login'))
    q = fetch_question(qid)
    if q is None:
        return "题目不存在"
    if request.method == 'POST':
        user_answer = request.form.getlist('answer')
        user_answer_str = "".join(sorted(user_answer))
        correct = 1 if user_answer_str == "".join(sorted(q['answer'])) else 0
        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO history (user_id, question_id, user_answer, correct) VALUES (?,?,?,?)',
                  (get_user_id(), qid, user_answer_str, correct))
        conn.commit()
        # 获取总题数和已答题数
        c.execute('SELECT COUNT(*) as total FROM questions')
        total = c.fetchone()['total']
        c.execute('SELECT COUNT(*) as answered FROM history WHERE user_id=?', (get_user_id(),))
        answered = c.fetchone()['answered']
        conn.close()
        result_msg = "回答正确" if correct == 1 else f"回答错误，正确答案：{q['answer']}"
        return render_template('question.html', question=q, result_msg=result_msg, answered=answered, total=total)
    
    # GET 请求时，获取进度数据
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as total FROM questions')
    total = c.fetchone()['total']
    c.execute('SELECT COUNT(*) as answered FROM history WHERE user_id=?', (get_user_id(),))
    answered = c.fetchone()['answered']
    conn.close()
    return render_template('question.html', question=q, answered=answered, total=total)


@app.route('/history')
def show_history():
    if not is_logged_in():
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM history WHERE user_id=? ORDER BY timestamp DESC', (get_user_id(),))
    rows = c.fetchall()
    history_data = []
    for r in rows:
        q = fetch_question(r['question_id'])
        stem = q['stem'] if q else ''
        history_data.append({
            'id': r['id'],
            'question_id': r['question_id'],
            'stem': stem,
            'user_answer': r['user_answer'],
            'correct': r['correct'],
            'timestamp': r['timestamp']
        })
    conn.close()
    return render_template('history.html', history=history_data)

@app.route('/search', methods=['GET','POST'])
def search():
    if not is_logged_in():
        return redirect(url_for('login'))
    query = request.form.get('query','')
    results = []
    if query:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM questions WHERE stem LIKE ?", ('%'+query+'%',))
        rows = c.fetchall()
        conn.close()
        for row in rows:
            q = {
                'id': row['id'],
                'stem': row['stem']
            }
            results.append(q)
    return render_template('search.html', query=query, results=results)

@app.route('/wrong')
def wrong_questions():
    if not is_logged_in():
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT question_id FROM history WHERE user_id=? AND correct=0', (get_user_id(),))
    rows = c.fetchall()
    wrong_ids = [r['question_id'] for r in rows]
    wrong_ids = set(wrong_ids)
    questions_list = []
    for qid in wrong_ids:
        q = fetch_question(qid)
        if q:
            questions_list.append(q)
    return render_template('wrong.html', questions=questions_list)

@app.route('/only_wrong')
def only_wrong_mode():
    if not is_logged_in():
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT question_id FROM history WHERE user_id=? AND correct=0', (get_user_id(),))
    rows = c.fetchall()
    wrong_ids = [r['question_id'] for r in rows]
    if not wrong_ids:
        return "你没有错题或还未答题"
    qid = random.choice(wrong_ids)
    q = fetch_question(qid)
    return render_template('question.html', question=q)

# ============= 分类与筛选功能 ==============
@app.route('/filter', methods=['GET','POST'])
def filter_questions():
    if not is_logged_in():
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    # 获取所有分类与难度，以便下拉选择
    c.execute('SELECT DISTINCT category FROM questions')
    categories = [r['category'] for r in c.fetchall()]
    c.execute('SELECT DISTINCT difficulty FROM questions')
    difficulties = [r['difficulty'] for r in c.fetchall()]

    selected_category = ''
    selected_difficulty = ''
    results = []
    if request.method == 'POST':
        selected_category = request.form.get('category','')
        selected_difficulty = request.form.get('difficulty','')
        sql = "SELECT id, stem FROM questions WHERE 1=1"
        params = []
        if selected_category:
            sql += " AND category=?"
            params.append(selected_category)
        if selected_difficulty:
            sql += " AND difficulty=?"
            params.append(selected_difficulty)
        c.execute(sql, params)
        rows = c.fetchall()
        for row in rows:
            results.append({'id': row['id'],'stem': row['stem']})

    conn.close()
    return render_template('filter.html', categories=categories, difficulties=difficulties,
                           selected_category=selected_category,
                           selected_difficulty=selected_difficulty,
                           results=results)

# ============= 收藏与标记功能 ==============
@app.route('/favorite/<qid>', methods=['POST'])
def favorite_question(qid):
    if not is_logged_in():
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO favorites (user_id, question_id, tag) VALUES (?,?,?)',
              (get_user_id(), qid, ''))
    conn.commit()
    conn.close()
    flash("收藏成功！")
    return redirect(url_for('show_question', qid=qid))

@app.route('/unfavorite/<qid>', methods=['POST'])
def unfavorite_question(qid):
    if not is_logged_in():
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM favorites WHERE user_id=? AND question_id=?', (get_user_id(), qid))
    conn.commit()
    conn.close()
    return "已取消收藏"

@app.route('/update_tag/<qid>', methods=['POST'])
def update_tag(qid):
    if not is_logged_in():
        return {"success": False, "msg": "未登录"}, 401
    new_tag = request.form.get('tag','')
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE favorites SET tag=? WHERE user_id=? AND question_id=?',
              (new_tag, get_user_id(), qid))
    conn.commit()
    conn.close()
    return {"success": True, "msg": "标记更新成功"}


@app.route('/favorites')
def show_favorites():
    if not is_logged_in():
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT f.question_id, f.tag, q.stem FROM favorites f JOIN questions q ON f.question_id=q.id WHERE f.user_id=?',
              (get_user_id(),))
    rows = c.fetchall()
    favorites_data = [{'question_id': r['question_id'], 'tag': r['tag'], 'stem': r['stem']} for r in rows]
    conn.close()
    return render_template('favorites.html', favorites=favorites_data)

# ============= 定时模式与模拟考试模式 ==============
# 简化实现：定时模式与模拟考试模式，随机抽取若干题组成一套题存session，计时器前端实现

@app.route('/modes')
def modes():
    # 简单模式选择页面
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('index.html', mode_select=True)  # 在index.html里增加选择模式链接

@app.route('/start_timed_mode', methods=['POST'])
def start_timed_mode():
    # 假设定时模式抽取5题，10分钟完成
    if not is_logged_in():
        return redirect(url_for('login'))
    question_ids = fetch_random_question_ids(5)
    start_time = datetime.now()
    duration = 600  # 10分钟
    # 存入 exam_sessions
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO exam_sessions (user_id, mode, question_ids, start_time, duration) VALUES (?,?,?,?,?)',
              (get_user_id(), 'timed', json.dumps(question_ids), start_time, duration))
    exam_id = c.lastrowid
    conn.commit()
    conn.close()
    session['current_exam_id'] = exam_id
    return redirect(url_for('timed_mode'))
@app.route('/sequential_start')
def sequential_start():
    if not is_logged_in():
        return redirect(url_for('login'))
    user_id = get_user_id()
    conn = get_db()
    c = conn.cursor()

    # 找到“第一道还没做过”的题目
    c.execute('''
        SELECT id FROM questions
        WHERE id NOT IN (
            SELECT question_id FROM history WHERE user_id=?
        )
        ORDER BY id ASC
        LIMIT 1
    ''', (user_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        flash("恭喜，题库已经全部做完！")
        return redirect(url_for('index'))

    current_qid = row['id']
    c.execute('UPDATE users SET current_seq_qid=? WHERE id=?',
              (current_qid, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('show_sequential_question', qid=current_qid))
@app.route('/sequential/<qid>', methods=['GET', 'POST'])
def show_sequential_question(qid):
    if not is_logged_in():
        return redirect(url_for('login'))

    q = fetch_question(qid)
    if q is None:
        return "题目不存在"

    user_id = get_user_id()
    next_qid = None
    result_msg = None

    if request.method == 'POST':
        user_answer = request.form.getlist('answer')
        user_answer_str = "".join(sorted(user_answer))
        correct = int(user_answer_str == "".join(sorted(q['answer'])))

        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO history (user_id, question_id, user_answer, correct) '
                  'VALUES (?,?,?,?)',
                  (user_id, qid, user_answer_str, correct))

        # 查找下一道【未做过】且 id 更大的题
        c.execute('''
            SELECT id FROM questions
            WHERE id>? AND id NOT IN (
                SELECT question_id FROM history WHERE user_id=?
            )
            ORDER BY id ASC LIMIT 1
        ''', (qid, user_id))
        row = c.fetchone()
        if row:
            next_qid = row['id']
            c.execute('UPDATE users SET current_seq_qid=? WHERE id=?',
                      (next_qid, user_id))
        else:
            # 没有剩余题目，把进度清零
            c.execute('UPDATE users SET current_seq_qid=NULL WHERE id=?',
                      (user_id,))
        conn.commit()
        conn.close()

        result_msg = "回答正确！" if correct else f"回答错误，正确答案：{q['answer']}"

    return render_template('question.html',
                           question=q,
                           result_msg=result_msg,
                           next_qid=next_qid,
                           sequential_mode=True)


@app.route('/timed_mode')
def timed_mode():
    if not is_logged_in():
        return redirect(url_for('login'))
    exam_id = session.get('current_exam_id')
    if not exam_id:
        return "未启动定时模式"
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM exam_sessions WHERE id=? AND user_id=?', (exam_id, get_user_id()))
    exam = c.fetchone()
    conn.close()
    if not exam:
        return "无法找到考试会话"
    question_ids = json.loads(exam['question_ids'])
    start_time = datetime.strptime(exam['start_time'], '%Y-%m-%d %H:%M:%S.%f')
    end_time = start_time + timedelta(seconds=exam['duration'])
    remaining = (end_time - datetime.now()).total_seconds()
    if remaining <= 0:
        # 时间到，自动提交
        return redirect(url_for('submit_timed_mode'))
    questions_list = [fetch_question(qid) for qid in question_ids]
    return render_template('timed_mode.html', questions=questions_list, remaining=remaining)

@app.route('/submit_timed_mode', methods=['POST','GET'])
def submit_timed_mode():
    if not is_logged_in():
        return redirect(url_for('login'))
    exam_id = session.get('current_exam_id')
    if not exam_id:
        return "没有正在进行的定时模式"
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM exam_sessions WHERE id=? AND user_id=?', (exam_id, get_user_id()))
    exam = c.fetchone()
    if not exam:
        return "无法找到考试会话"
    question_ids = json.loads(exam['question_ids'])

    # 收集用户提交答案
    # POST过来可以是`answer_<qid>`的形式
    correct_count = 0
    total = len(question_ids)
    for qid in question_ids:
        user_answer = request.form.getlist(f'answer_{qid}')
        q = fetch_question(qid)
        if not q:
            continue
        user_answer_str = "".join(sorted(user_answer))
        correct = 1 if user_answer_str == "".join(sorted(q['answer'])) else 0
        if correct:
            correct_count += 1
        # 保存history
        c.execute('INSERT INTO history (user_id, question_id, user_answer, correct) VALUES (?,?,?,?)',
                  (get_user_id(), qid, user_answer_str, correct))

    conn.commit()
    conn.close()

    session.pop('current_exam_id', None)
    score = correct_count / total * 100
    return f"定时模式结束！正确率：{correct_count}/{total} = {score:.2f}%"

def fetch_random_question_ids(num):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id FROM questions ORDER BY RANDOM() LIMIT ?', (num,))
    rows = c.fetchall()
    conn.close()
    return [r['id'] for r in rows]

@app.route('/start_exam', methods=['POST'])
def start_exam():
    if not is_logged_in():
        return redirect(url_for('login'))
    # 模拟考试，比如抽取10题，无时间限制，也可添加时间
    question_ids = fetch_random_question_ids(10)
    start_time = datetime.now()
    duration = 0  # 0表示无时间限制
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO exam_sessions (user_id, mode, question_ids, start_time, duration) VALUES (?,?,?,?,?)',
              (get_user_id(), 'exam', json.dumps(question_ids), start_time, duration))
    exam_id = c.lastrowid
    conn.commit()
    conn.close()
    session['current_exam_id'] = exam_id
    return redirect(url_for('exam'))

@app.route('/exam')
def exam():
    if not is_logged_in():
        return redirect(url_for('login'))
    exam_id = session.get('current_exam_id')
    if not exam_id:
        return "未启动考试模式"
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM exam_sessions WHERE id=? AND user_id=?', (exam_id, get_user_id()))
    exam = c.fetchone()
    conn.close()
    if not exam:
        return "无法找到考试"
    question_ids = json.loads(exam['question_ids'])
    questions_list = [fetch_question(qid) for qid in question_ids]
    return render_template('exam.html', questions=questions_list)

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    if not is_logged_in():
        return redirect(url_for('login'))
    exam_id = session.get('current_exam_id')
    if not exam_id:
        return "没有正在进行的考试"
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM exam_sessions WHERE id=? AND user_id=?', (exam_id, get_user_id()))
    exam = c.fetchone()
    if not exam:
        return "无法找到考试"

    question_ids = json.loads(exam['question_ids'])
    correct_count = 0
    total = len(question_ids)
    for qid in question_ids:
        user_answer = request.form.getlist(f'answer_{qid}')
        q = fetch_question(qid)
        if not q:
            continue
        user_answer_str = "".join(sorted(user_answer))
        correct = 1 if user_answer_str == "".join(sorted(q['answer'])) else 0
        if correct:
            correct_count += 1
        c.execute('INSERT INTO history (user_id, question_id, user_answer, correct) VALUES (?,?,?,?)',
                  (get_user_id(), qid, user_answer_str, correct))
    conn.commit()
    conn.close()
    session.pop('current_exam_id', None)
    score = correct_count / total * 100 if total > 0 else 0

    # 不返回普通文本，改为JSON响应
    return {
        "success": True,
        "correct_count": correct_count,
        "total": total,
        "score": score
    }

# ============= 统计与反馈 ==============
@app.route('/statistics')
def statistics():
    if not is_logged_in():
        return redirect(url_for('login'))
    user_id = get_user_id()
    conn = get_db()
    c = conn.cursor()
    # 总体正确率
    c.execute('SELECT COUNT(*) as total, SUM(correct) as correct_count FROM history WHERE user_id=?', (user_id,))
    row = c.fetchone()
    total = row['total'] if row['total'] else 0
    correct_count = row['correct_count'] if row['correct_count'] else 0
    overall_accuracy = (correct_count/total*100) if total>0 else 0

    # 按难度统计
    c.execute('''SELECT q.difficulty, COUNT(*) as total, SUM(h.correct) as correct_count
                 FROM history h JOIN questions q ON h.question_id=q.id
                 WHERE h.user_id=?
                 GROUP BY q.difficulty''', (user_id,))
    difficulty_stats = []
    for r in c.fetchall():
        difficulty_stats.append({
            'difficulty': r['difficulty'],
            'total': r['total'],
            'correct_count': r['correct_count'],
            'accuracy': (r['correct_count']/r['total']*100) if r['total']>0 else 0
        })

    # 错题排行
    c.execute('''SELECT h.question_id, COUNT(*) as wrong_times, q.stem
                 FROM history h JOIN questions q ON h.question_id=q.id
                 WHERE h.user_id=? AND h.correct=0
                 GROUP BY h.question_id
                 ORDER BY wrong_times DESC
                 LIMIT 10''', (user_id,))
    worst_questions = []
    for r in c.fetchall():
        worst_questions.append({
            'question_id': r['question_id'],
            'stem': r['stem'],
            'wrong_times': r['wrong_times']
        })

    conn.close()
    return render_template('statistics.html', 
                           overall_accuracy=overall_accuracy,
                           difficulty_stats=difficulty_stats,
                           worst_questions=worst_questions)

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True, port=32217)
