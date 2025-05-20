#!/usr/bin/env python3
"""
EXAM-MASTER - A Flask-based Online Quiz System

This application provides a complete quiz system with features including:
- User registration and authentication
- Question management with import from CSV
- Multiple quiz modes (random, sequential, timed, exam)
- User progress tracking and statistics
- Favorites, tags, and search functionality

Author: ShayneChen (xinyu-c@outlook.com)
License: MIT
"""

# Standard library imports
import csv
import json
import os
import random
import sqlite3
import time
from datetime import datetime, timedelta
from functools import wraps

# Third-party imports
from flask import (
    Flask, 
    request, 
    render_template, 
    session, 
    redirect, 
    url_for, 
    flash, 
    jsonify, 
    abort
)
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask application
app = Flask(__name__)
# Use environment variable for secret key with a fallback default
# In production, always set this through environment variables
app.secret_key = os.environ.get('SECRET_KEY', 'change_this_in_production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

#############################
# Database Helper Functions #
#############################

def get_db():
    """
    Create a database connection and configure it to return rows as dictionaries.
    
    Returns:
        sqlite3.Connection: The configured database connection
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialize the database by creating necessary tables if they don't exist.
    Also loads initial question data from CSV if the questions table is empty.
    """
    conn = get_db()
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        current_seq_qid TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # History table for tracking user answers
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question_id TEXT NOT NULL,
        user_answer TEXT NOT NULL,
        correct INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Questions table for storing question data
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
        id TEXT PRIMARY KEY,
        stem TEXT NOT NULL,
        answer TEXT NOT NULL,
        difficulty TEXT,
        qtype TEXT,
        category TEXT,
        options TEXT, -- JSON stored options
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Favorites table for user bookmarks
    c.execute('''CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question_id TEXT NOT NULL,
        tag TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, question_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    )''')
    
    # Exam sessions table for timed mode and exams
    c.execute('''CREATE TABLE IF NOT EXISTS exam_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        mode TEXT NOT NULL, -- 'exam' or 'timed'
        question_ids TEXT NOT NULL, -- JSON list
        start_time DATETIME NOT NULL,
        duration INTEGER NOT NULL, -- seconds
        completed BOOLEAN DEFAULT 0,
        score REAL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    conn.commit()

    # Load questions from CSV if the table is empty
    c.execute('SELECT COUNT(*) as cnt FROM questions')
    if c.fetchone()['cnt'] == 0:
        load_questions_to_db(conn)
    
    conn.close()

def load_questions_to_db(conn):
    """
    Load questions from a CSV file into the database.
    
    Args:
        conn (sqlite3.Connection): The database connection
    """
    try:
        with open('questions.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            c = conn.cursor()
            for row in reader:
                options = {}
                for opt in ['A', 'B', 'C', 'D', 'E']:
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
    except FileNotFoundError:
        print("Warning: questions.csv file not found. No questions loaded.")
    except Exception as e:
        print(f"Error loading questions: {e}")

# Initialize the database
init_db()

################################
# Authentication Helper Functions #
################################

def login_required(f):
    """
    Decorator to require login for a route.
    
    Args:
        f (function): The route function to decorate
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            flash("请先登录后再访问该页面", "error")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def is_logged_in():
    """
    Check if the user is logged in.
    
    Returns:
        bool: True if user is logged in, False otherwise
    """
    return 'user_id' in session

def get_user_id():
    """
    Get the current user's ID from the session.
    
    Returns:
        int: The user ID if logged in, None otherwise
    """
    return session.get('user_id')

##############################
# Question Helper Functions #
##############################

def fetch_question(qid):
    """
    Fetch a question by ID from the database.
    
    Args:
        qid (str): The question ID
        
    Returns:
        dict: The question data or None if not found
    """
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM questions WHERE id=?', (qid,))
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
    """
    Get a random question ID for a user, excluding questions they've already answered.
    
    Args:
        user_id (int): The user ID
        
    Returns:
        str: A random question ID or None if all questions have been answered
    """
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

def fetch_random_question_ids(num):
    """
    Fetch multiple random question IDs.
    
    Args:
        num (int): The number of question IDs to fetch
        
    Returns:
        list: A list of random question IDs
    """
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id FROM questions ORDER BY RANDOM() LIMIT ?', (num,))
    rows = c.fetchall()
    conn.close()
    return [r['id'] for r in rows]

def is_favorite(user_id, question_id):
    """
    Check if a question is favorited by a user.
    
    Args:
        user_id (int): The user ID
        question_id (str): The question ID
        
    Returns:
        bool: True if favorited, False otherwise
    """
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT 1 FROM favorites WHERE user_id=? AND question_id=?',
              (user_id, question_id))
    is_fav = bool(c.fetchone())
    conn.close()
    return is_fav

##############################
# Authentication Routes #
##############################

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Route for user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Input validation
        if not username or not password:
            flash("用户名和密码不能为空", "error")
            return render_template('register.html')
            
        if password != confirm_password:
            flash("两次输入的密码不一致", "error")
            return render_template('register.html')
            
        if len(password) < 6:
            flash("密码长度不能少于6个字符", "error")
            return render_template('register.html')
        
        conn = get_db()
        c = conn.cursor()
        
        # Check if username exists
        c.execute('SELECT id FROM users WHERE username=?', (username,))
        if c.fetchone():
            conn.close()
            flash("用户名已存在，请更换用户名", "error")
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        c.execute('INSERT INTO users (username, password_hash) VALUES (?,?)', 
                  (username, password_hash))
        conn.commit()
        conn.close()
        
        flash("注册成功，请登录", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Route for user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash("用户名和密码不能为空", "error")
            return render_template('login.html')
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT id, password_hash FROM users WHERE username=?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            
            # Redirect to 'next' parameter if provided
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
                
            return redirect(url_for('index'))
        else:
            flash("登录失败，用户名或密码错误", "error")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Route for user logout."""
    session.clear()
    flash("您已成功退出登录", "success")
    return redirect(url_for('login'))

##############################
# Main Application Routes #
##############################

@app.route('/')
@login_required
def index():
    """Home page route."""
    return render_template('index.html', current_year=datetime.now().year)

@app.route('/reset_history', methods=['POST'])
@login_required
def reset_history():
    """Route to reset a user's answer history."""
    user_id = get_user_id()
    
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('DELETE FROM history WHERE user_id=?', (user_id,))
        conn.commit()
        conn.close()
        flash("答题历史已重置。现在您可以重新开始答题。", "success")
    except Exception as e:
        flash(f"重置历史时出错: {str(e)}", "error")
        
    return redirect(url_for('random_question'))

##############################
# Question Routes #
##############################

@app.route('/random', methods=['GET'])
@login_required
def random_question():
    """Route to get a random question."""
    user_id = get_user_id()
    qid = random_question_id(user_id)
    
    conn = get_db()
    c = conn.cursor()
    # Get total questions count
    c.execute('SELECT COUNT(*) as total FROM questions')
    total = c.fetchone()['total']
    # Get answered questions count
    c.execute('SELECT COUNT(DISTINCT question_id) as answered FROM history WHERE user_id=?', (user_id,))
    answered = c.fetchone()['answered']
    conn.close()
    
    if not qid:
        flash("您已完成所有题目！可以重置历史以重新开始。", "info")
        return render_template('question.html', question=None, answered=answered, total=total)
        
    q = fetch_question(qid)
    is_fav = is_favorite(user_id, qid)
    
    return render_template('question.html', 
                          question=q, 
                          answered=answered, 
                          total=total,
                          is_favorite=is_fav)

@app.route('/question/<qid>', methods=['GET', 'POST'])
@login_required
def show_question(qid):
    """Route to view and answer a specific question."""
    user_id = get_user_id()
    q = fetch_question(qid)
    
    if q is None:
        flash("题目不存在", "error")
        return redirect(url_for('index'))

    # Handle form submission (answer)
    if request.method == 'POST':
        user_answer = request.form.getlist('answer')
        user_answer_str = "".join(sorted(user_answer))
        correct = int(user_answer_str == "".join(sorted(q['answer'])))

        conn = get_db()
        c = conn.cursor()
        
        # Save answer to history
        c.execute(
            'INSERT INTO history (user_id, question_id, user_answer, correct) VALUES (?,?,?,?)',
            (user_id, qid, user_answer_str, correct)
        )
        conn.commit()

        # Get updated stats
        c.execute('SELECT COUNT(*) AS total FROM questions')
        total = c.fetchone()['total']
        c.execute('SELECT COUNT(DISTINCT question_id) AS answered FROM history WHERE user_id=?', (user_id,))
        answered = c.fetchone()['answered']
        conn.close()

        result_msg = "回答正确" if correct else f"回答错误，正确答案：{q['answer']}"
        flash(result_msg, "success" if correct else "error")
        
        is_fav = is_favorite(user_id, qid)
        
        return render_template('question.html',
                              question=q,
                              result_msg=result_msg,
                              answered=answered,
                              total=total,
                              is_favorite=is_fav)

    # Handle GET request
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) AS total FROM questions')
    total = c.fetchone()['total']
    c.execute('SELECT COUNT(DISTINCT question_id) AS answered FROM history WHERE user_id=?', (user_id,))
    answered = c.fetchone()['answered']
    conn.close()
    
    is_fav = is_favorite(user_id, qid)

    return render_template('question.html',
                          question=q,
                          answered=answered,
                          total=total,
                          is_favorite=is_fav)

@app.route('/history')
@login_required
def show_history():
    """Route to view answer history."""
    user_id = get_user_id()
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM history WHERE user_id=? ORDER BY timestamp DESC', (user_id,))
    rows = c.fetchall()
    conn.close()
    
    history_data = []
    for r in rows:
        q = fetch_question(r['question_id'])
        stem = q['stem'] if q else '题目已删除'
        history_data.append({
            'id': r['id'],
            'question_id': r['question_id'],
            'stem': stem,
            'user_answer': r['user_answer'],
            'correct': r['correct'],
            'timestamp': r['timestamp']
        })
    
    return render_template('history.html', history=history_data)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Route to search for questions by keyword."""
    query = request.form.get('query', '')
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
@login_required
def wrong_questions():
    """Route to view wrong answers."""
    user_id = get_user_id()
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT question_id FROM history WHERE user_id=? AND correct=0', (user_id,))
    rows = c.fetchall()
    conn.close()
    
    wrong_ids = set(r['question_id'] for r in rows)
    questions_list = []
    
    for qid in wrong_ids:
        q = fetch_question(qid)
        if q:
            questions_list.append(q)
    
    return render_template('wrong.html', questions=questions_list)

@app.route('/only_wrong')
@login_required
def only_wrong_mode():
    """Route to practice only wrong questions."""
    user_id = get_user_id()
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT question_id FROM history WHERE user_id=? AND correct=0', (user_id,))
    rows = c.fetchall()
    conn.close()
    
    wrong_ids = [r['question_id'] for r in rows]
    
    if not wrong_ids:
        flash("你没有错题或还未答题", "info")
        return redirect(url_for('index'))
    
    qid = random.choice(wrong_ids)
    q = fetch_question(qid)
    is_fav = is_favorite(user_id, qid)
    
    return render_template('question.html', 
                          question=q, 
                          is_favorite=is_fav)

##############################
# Filter Routes #
##############################

@app.route('/filter', methods=['GET', 'POST'])
@login_required
def filter_questions():
    """Route to filter questions by category and difficulty."""
    conn = get_db()
    c = conn.cursor()
    
    # Get all categories and difficulties for dropdown selection
    c.execute('SELECT DISTINCT category FROM questions WHERE category IS NOT NULL AND category != ""')
    categories = [r['category'] for r in c.fetchall()]
    
    c.execute('SELECT DISTINCT difficulty FROM questions WHERE difficulty IS NOT NULL AND difficulty != ""')
    difficulties = [r['difficulty'] for r in c.fetchall()]

    selected_category = ''
    selected_difficulty = ''
    results = []
    
    if request.method == 'POST':
        selected_category = request.form.get('category', '')
        selected_difficulty = request.form.get('difficulty', '')
        
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
            results.append({'id': row['id'], 'stem': row['stem']})

    conn.close()
    
    return render_template('filter.html', 
                          categories=categories, 
                          difficulties=difficulties,
                          selected_category=selected_category,
                          selected_difficulty=selected_difficulty,
                          results=results)

##############################
# Favorites Routes #
##############################

@app.route('/favorite/<qid>', methods=['POST'])
@login_required
def favorite_question(qid):
    """Route to add a question to favorites."""
    user_id = get_user_id()
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('INSERT OR IGNORE INTO favorites (user_id, question_id, tag) VALUES (?,?,?)',
                  (user_id, qid, ''))
        conn.commit()
        flash("收藏成功！", "success")
    except Exception as e:
        flash(f"收藏失败: {str(e)}", "error")
    finally:
        conn.close()
    
    # Redirect back to the question page
    referrer = request.referrer
    if referrer and '/question/' in referrer:
        return redirect(referrer)
    return redirect(url_for('show_question', qid=qid))

@app.route('/unfavorite/<qid>', methods=['POST'])
@login_required
def unfavorite_question(qid):
    """Route to remove a question from favorites."""
    user_id = get_user_id()
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('DELETE FROM favorites WHERE user_id=? AND question_id=?', 
                  (user_id, qid))
        conn.commit()
        flash("已取消收藏", "success")
    except Exception as e:
        flash(f"取消收藏失败: {str(e)}", "error")
    finally:
        conn.close()
    
    # Redirect back to the question page
    referrer = request.referrer
    if referrer and '/question/' in referrer:
        return redirect(referrer)
    return redirect(url_for('show_question', qid=qid))

@app.route('/update_tag/<qid>', methods=['POST'])
@login_required
def update_tag(qid):
    """API route to update a favorite's tag."""
    if not is_logged_in():
        return jsonify({"success": False, "msg": "未登录"}), 401
    
    user_id = get_user_id()
    new_tag = request.form.get('tag', '')
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('UPDATE favorites SET tag=? WHERE user_id=? AND question_id=?',
                  (new_tag, user_id, qid))
        conn.commit()
        return jsonify({"success": True, "msg": "标记更新成功"})
    except Exception as e:
        return jsonify({"success": False, "msg": f"更新失败: {str(e)}"}), 500
    finally:
        conn.close()

@app.route('/favorites')
@login_required
def show_favorites():
    """Route to view favorites."""
    user_id = get_user_id()
    
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT f.question_id, f.tag, q.stem 
        FROM favorites f 
        JOIN questions q ON f.question_id=q.id 
        WHERE f.user_id=?
    ''', (user_id,))
    
    rows = c.fetchall()
    conn.close()
    
    favorites_data = [
        {'question_id': r['question_id'], 'tag': r['tag'], 'stem': r['stem']} 
        for r in rows
    ]
    
    return render_template('favorites.html', favorites=favorites_data)

##############################
# Sequential Mode Routes #
##############################

@app.route('/sequential_start')
@login_required
def sequential_start():
    """Route to start or continue sequential answering mode."""
    user_id = get_user_id()
    conn = get_db()
    c = conn.cursor()

    # Check if user has a saved position
    c.execute('SELECT current_seq_qid FROM users WHERE id=?', (user_id,))
    user_data = c.fetchone()
    
    if user_data and user_data['current_seq_qid']:
        # Continue from saved position
        current_qid = user_data['current_seq_qid']
    else:
        # Find the first unanswered question
        c.execute('''
            SELECT id
            FROM questions
            WHERE id NOT IN (
                SELECT question_id FROM history WHERE user_id = ?
            )
            ORDER BY CAST(id AS INTEGER) ASC
            LIMIT 1
        ''', (user_id,))
        row = c.fetchone()
        
        if row is None:
            conn.close()
            flash("恭喜，题库已经全部做完！", "success")
            return redirect(url_for('index'))
            
        current_qid = row['id']
        
        # Save the position
        c.execute(
            'UPDATE users SET current_seq_qid = ? WHERE id = ?',
            (current_qid, user_id)
        )
        conn.commit()
    
    conn.close()
    return redirect(url_for('show_sequential_question', qid=current_qid))

@app.route('/sequential/<qid>', methods=['GET', 'POST'])
@login_required
def show_sequential_question(qid):
    """Route to show and handle sequential questions."""
    user_id = get_user_id()
    q = fetch_question(qid)
    
    if q is None:
        flash("题目不存在", "error")
        return redirect(url_for('index'))

    next_qid = None
    result_msg = None
    user_answer_str = ""
    
    conn = get_db()
    c = conn.cursor()
    
    # Handle POST request (user submitted an answer)
    if request.method == 'POST':
        user_answer = request.form.getlist('answer')
        user_answer_str = "".join(sorted(user_answer))
        correct = int(user_answer_str == "".join(sorted(q['answer'])))
        
        # Save answer to history
        c.execute('INSERT INTO history (user_id, question_id, user_answer, correct) '
                  'VALUES (?,?,?,?)',
                  (user_id, qid, user_answer_str, correct))
        
        # Find next unanswered question with higher ID
        c.execute('''
            SELECT id FROM questions
            WHERE CAST(id AS INTEGER) > ?
              AND id NOT IN (
                  SELECT question_id FROM history WHERE user_id = ?
              )
            ORDER BY CAST(id AS INTEGER) ASC
            LIMIT 1
        ''', (int(qid), user_id))
        
        row = c.fetchone()
        if row:
            next_qid = row['id']
            c.execute('UPDATE users SET current_seq_qid = ? WHERE id = ?',
                      (next_qid, user_id))
        else:
            c.execute('UPDATE users SET current_seq_qid = NULL WHERE id = ?',
                      (user_id,))
            
        result_msg = "回答正确！" if correct else f"回答错误，正确答案：{q['answer']}"
        flash(result_msg, "success" if correct else "error")
    
    # Get progress statistics
    c.execute('SELECT COUNT(*) AS total FROM questions')
    total = c.fetchone()['total']
    
    c.execute('SELECT COUNT(DISTINCT question_id) AS answered '
              'FROM history WHERE user_id = ?', (user_id,))
    answered = c.fetchone()['answered']
    
    conn.commit()
    conn.close()
    
    is_fav = is_favorite(user_id, qid)
    
    return render_template('question.html',
                          question=q,
                          result_msg=result_msg,
                          next_qid=next_qid,
                          sequential_mode=True,
                          user_answer=user_answer_str,
                          answered=answered,
                          total=total,
                          is_favorite=is_fav)

##############################
# Timed Mode & Exam Routes #
##############################

@app.route('/modes')
@login_required
def modes():
    """Route to select quiz mode."""
    return render_template('index.html', mode_select=True, current_year=datetime.now().year)

@app.route('/start_timed_mode', methods=['POST'])
@login_required
def start_timed_mode():
    """Route to start timed mode quiz."""
    user_id = get_user_id()
    
    # Configuration for timed mode
    question_count = int(request.form.get('question_count', 5))
    duration_minutes = int(request.form.get('duration', 10))
    
    question_ids = fetch_random_question_ids(question_count)
    start_time = datetime.now()
    duration = duration_minutes * 60  # Convert minutes to seconds
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO exam_sessions 
            (user_id, mode, question_ids, start_time, duration) 
            VALUES (?,?,?,?,?)
        ''', (user_id, 'timed', json.dumps(question_ids), start_time, duration))
        
        exam_id = c.lastrowid
        conn.commit()
        session['current_exam_id'] = exam_id
        
        return redirect(url_for('timed_mode'))
    except Exception as e:
        flash(f"启动定时模式失败: {str(e)}", "error")
        return redirect(url_for('index'))
    finally:
        conn.close()

@app.route('/timed_mode')
@login_required
def timed_mode():
    """Route for timed mode quiz interface."""
    user_id = get_user_id()
    exam_id = session.get('current_exam_id')
    
    if not exam_id:
        flash("未启动定时模式", "error")
        return redirect(url_for('index'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM exam_sessions WHERE id=? AND user_id=?', (exam_id, user_id))
    exam = c.fetchone()
    conn.close()
    
    if not exam:
        flash("无法找到考试会话", "error")
        return redirect(url_for('index'))
    
    question_ids = json.loads(exam['question_ids'])
    start_time = datetime.strptime(exam['start_time'], '%Y-%m-%d %H:%M:%S.%f')
    end_time = start_time + timedelta(seconds=exam['duration'])
    
    remaining = (end_time - datetime.now()).total_seconds()
    if remaining <= 0:
        # Time's up, auto-submit
        return redirect(url_for('submit_timed_mode'))
    
    questions_list = [fetch_question(qid) for qid in question_ids]
    return render_template('timed_mode.html', questions=questions_list, remaining=remaining)

@app.route('/submit_timed_mode', methods=['POST', 'GET'])
@login_required
def submit_timed_mode():
    """Route to submit answers from timed mode."""
    user_id = get_user_id()
    exam_id = session.get('current_exam_id')
    
    if not exam_id:
        flash("没有正在进行的定时模式", "error")
        return redirect(url_for('index'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM exam_sessions WHERE id=? AND user_id=?', (exam_id, user_id))
    exam = c.fetchone()
    
    if not exam:
        conn.close()
        flash("无法找到考试会话", "error")
        return redirect(url_for('index'))
    
    question_ids = json.loads(exam['question_ids'])
    
    # Process answers
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
            
        # Save to history
        c.execute('INSERT INTO history (user_id, question_id, user_answer, correct) VALUES (?,?,?,?)',
                  (user_id, qid, user_answer_str, correct))
    
    # Mark session as completed and save score
    score = (correct_count / total * 100) if total > 0 else 0
    c.execute('UPDATE exam_sessions SET completed=1, score=? WHERE id=?', (score, exam_id))
    conn.commit()
    conn.close()
    
    # Clear session
    session.pop('current_exam_id', None)
    
    flash(f"定时模式结束！正确率：{correct_count}/{total} = {score:.2f}%", 
          "success" if score >= 60 else "error")
    
    return redirect(url_for('statistics'))

@app.route('/start_exam', methods=['POST'])
@login_required
def start_exam():
    """Route to start exam mode."""
    user_id = get_user_id()
    
    # Configuration
    question_count = int(request.form.get('question_count', 10))
    
    question_ids = fetch_random_question_ids(question_count)
    start_time = datetime.now()
    duration = 0  # 0 means no time limit
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO exam_sessions 
            (user_id, mode, question_ids, start_time, duration) 
            VALUES (?,?,?,?,?)
        ''', (user_id, 'exam', json.dumps(question_ids), start_time, duration))
        
        exam_id = c.lastrowid
        conn.commit()
        session['current_exam_id'] = exam_id
        
        return redirect(url_for('exam'))
    except Exception as e:
        flash(f"启动模拟考试失败: {str(e)}", "error")
        return redirect(url_for('index'))
    finally:
        conn.close()

@app.route('/exam')
@login_required
def exam():
    """Route for exam mode interface."""
    user_id = get_user_id()
    exam_id = session.get('current_exam_id')
    
    if not exam_id:
        flash("未启动考试模式", "error")
        return redirect(url_for('index'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM exam_sessions WHERE id=? AND user_id=?', (exam_id, user_id))
    exam = c.fetchone()
    conn.close()
    
    if not exam:
        flash("无法找到考试", "error")
        return redirect(url_for('index'))
    
    question_ids = json.loads(exam['question_ids'])
    questions_list = [fetch_question(qid) for qid in question_ids]
    
    return render_template('exam.html', questions=questions_list)

@app.route('/submit_exam', methods=['POST'])
@login_required
def submit_exam():
    """Route to submit answers from exam mode."""
    user_id = get_user_id()
    exam_id = session.get('current_exam_id')
    
    if not exam_id:
        return jsonify({
            "success": False,
            "msg": "没有正在进行的考试"
        }), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM exam_sessions WHERE id=? AND user_id=?', (exam_id, user_id))
    exam = c.fetchone()
    
    if not exam:
        conn.close()
        return jsonify({
            "success": False,
            "msg": "无法找到考试"
        }), 404
    
    question_ids = json.loads(exam['question_ids'])
    
    # Process answers
    correct_count = 0
    total = len(question_ids)
    question_results = []
    
    for qid in question_ids:
        user_answer = request.form.getlist(f'answer_{qid}')
        q = fetch_question(qid)
        
        if not q:
            continue
            
        user_answer_str = "".join(sorted(user_answer))
        correct = 1 if user_answer_str == "".join(sorted(q['answer'])) else 0
        
        if correct:
            correct_count += 1
            
        # Save to history
        c.execute('INSERT INTO history (user_id, question_id, user_answer, correct) VALUES (?,?,?,?)',
                  (user_id, qid, user_answer_str, correct))
        
        # Add to results
        question_results.append({
            "id": qid,
            "stem": q['stem'],
            "user_answer": user_answer_str,
            "correct_answer": q['answer'],
            "is_correct": correct == 1
        })
    
    # Mark session as completed and save score
    score = (correct_count / total * 100) if total > 0 else 0
    c.execute('UPDATE exam_sessions SET completed=1, score=? WHERE id=?', (score, exam_id))
    conn.commit()
    conn.close()
    
    # Clear session
    session.pop('current_exam_id', None)
    
    # Return detailed results
    return jsonify({
        "success": True,
        "correct_count": correct_count,
        "total": total,
        "score": score,
        "results": question_results
    })

##############################
# Statistics Routes #
##############################

@app.route('/statistics')
@login_required
def statistics():
    """Route to view user statistics."""
    user_id = get_user_id()
    conn = get_db()
    c = conn.cursor()
    
    # Overall accuracy
    c.execute('''
        SELECT 
            COUNT(*) as total, 
            SUM(correct) as correct_count 
        FROM history 
        WHERE user_id=?
    ''', (user_id,))
    
    row = c.fetchone()
    total = row['total'] if row['total'] else 0
    correct_count = row['correct_count'] if row['correct_count'] else 0
    overall_accuracy = (correct_count/total*100) if total>0 else 0
    
    # Stats by difficulty
    c.execute('''
        SELECT 
            q.difficulty, 
            COUNT(*) as total, 
            SUM(h.correct) as correct_count
        FROM history h 
        JOIN questions q ON h.question_id=q.id
        WHERE h.user_id=?
        GROUP BY q.difficulty
    ''', (user_id,))
    
    difficulty_stats = []
    for r in c.fetchall():
        difficulty_stats.append({
            'difficulty': r['difficulty'] or '未分类',
            'total': r['total'],
            'correct_count': r['correct_count'],
            'accuracy': (r['correct_count']/r['total']*100) if r['total']>0 else 0
        })
    
    # Stats by category
    c.execute('''
        SELECT 
            q.category, 
            COUNT(*) as total, 
            SUM(h.correct) as correct_count
        FROM history h 
        JOIN questions q ON h.question_id=q.id
        WHERE h.user_id=?
        GROUP BY q.category
    ''', (user_id,))
    
    category_stats = []
    for r in c.fetchall():
        category_stats.append({
            'category': r['category'] or '未分类',
            'total': r['total'],
            'correct_count': r['correct_count'],
            'accuracy': (r['correct_count']/r['total']*100) if r['total']>0 else 0
        })
    
    # Most wrong questions
    c.execute('''
        SELECT 
            h.question_id, 
            COUNT(*) as wrong_times, 
            q.stem
        FROM history h 
        JOIN questions q ON h.question_id=q.id
        WHERE h.user_id=? AND h.correct=0
        GROUP BY h.question_id
        ORDER BY wrong_times DESC
        LIMIT 10
    ''', (user_id,))
    
    worst_questions = []
    for r in c.fetchall():
        worst_questions.append({
            'question_id': r['question_id'],
            'stem': r['stem'],
            'wrong_times': r['wrong_times']
        })
    
    # Recent exams
    c.execute('''
        SELECT 
            id, 
            mode, 
            start_time, 
            score, 
            (SELECT COUNT(*) FROM JSON_EACH(question_ids)) as question_count
        FROM exam_sessions
        WHERE user_id=? AND completed=1
        ORDER BY start_time DESC
        LIMIT 5
    ''', (user_id,))
    
    recent_exams = []
    for r in c.fetchall():
        recent_exams.append({
            'id': r['id'],
            'mode': r['mode'],
            'start_time': r['start_time'],
            'score': r['score'],
            'question_count': r['question_count']
        })
    
    conn.close()
    
    return render_template('statistics.html', 
                          overall_accuracy=overall_accuracy,
                          difficulty_stats=difficulty_stats,
                          category_stats=category_stats,
                          worst_questions=worst_questions,
                          recent_exams=recent_exams)

##############################
# Error Handlers #
##############################

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('error.html', 
                          error_code=404, 
                          error_message="页面不存在"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('error.html', 
                          error_code=500, 
                          error_message="服务器内部错误"), 500

##############################
# Application Entry Point #
##############################

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=32217)