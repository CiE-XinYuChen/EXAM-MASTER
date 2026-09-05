"""SQLite storage, question formats and the shared CSV format."""
import csv
import io
import json
import re
import sqlite3

from flask import current_app, g

TYPES = ('单选题', '多选题', '判断题', '填空题')
LETTERS = 'ABCDE'
FIELDS = ('id', 'stem', 'answer', 'difficulty', 'qtype', 'category', 'options', 'explanation')
CSV_FIELDS = ['题号', '题干', *LETTERS, '答案', '难度', '题型', '类别', '解析']
UPSERT = f'''INSERT INTO questions ({','.join(FIELDS)}) VALUES ({','.join('?' for _ in FIELDS)})
    ON CONFLICT(id) DO UPDATE SET {','.join(f'{key}=excluded.{key}' for key in FIELDS[1:])}'''


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    conn = g.pop('db', None)
    if conn is not None:
        conn.close()


def query(sql, params=(), one=False):
    rows = [dict(row) for row in get_db().execute(sql, params)]
    return (rows[0] if rows else None) if one else rows


def init_db():
    fresh = not query("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, current_seq_qid TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY, stem TEXT NOT NULL, answer TEXT NOT NULL, difficulty TEXT,
            qtype TEXT, category TEXT, options TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, question_id TEXT NOT NULL,
            user_answer TEXT NOT NULL, correct INTEGER NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, question_id TEXT NOT NULL,
            tag TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id, question_id));
        CREATE TABLE IF NOT EXISTS exam_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, mode TEXT NOT NULL,
            question_ids TEXT NOT NULL, start_time TEXT NOT NULL, duration INTEGER NOT NULL,
            completed INTEGER DEFAULT 0, score REAL);
    ''')
    for table, column in [('questions', 'explanation'), ('exam_sessions', 'paper')]:
        if column not in {row['name'] for row in query(f'PRAGMA table_info({table})')}:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} TEXT NOT NULL DEFAULT ''")
    conn.commit()
    source = current_app.config.get('SEED_CSV')
    if fresh and source:
        with open(source, encoding='utf-8-sig', newline='') as handle:
            import_csv(handle.read())


def normalize_answer(value, qtype):
    value = value.strip()
    if qtype == '多选题':
        return ''.join(sorted(set(re.sub(r'[\s,，、;；]+', '', value.upper()))))
    if qtype == '单选题':
        return value.upper()
    if qtype == '判断题':
        aliases = {'a': '正确', 'true': '正确', '对': '正确', '是': '正确', '√': '正确', '1': '正确',
                   'b': '错误', 'false': '错误', '错': '错误', '否': '错误', '×': '错误', '0': '错误'}
        return aliases.get(value.lower(), value)
    return value


def unpack(row):
    row = dict(row)
    row['options'] = json.loads(row.get('options') or '{}')
    if row['qtype'] == '判断题':
        row['options'] = {'正确': '正确', '错误': '错误'}
    row['answer'] = normalize_answer(row['answer'], row['qtype'])
    row['issue'] = ('缺少题干' if not row['stem'].strip() else
                    '缺少答案' if not row['answer'] else
                    '选择题缺少选项' if row['qtype'] in TYPES[:2] and len(row['options']) < 2 else
                    '单选题有多个答案' if row['qtype'] == '单选题' and len(row['answer']) != 1 else
                    '判断题答案无效' if row['qtype'] == '判断题' and row['answer'] not in ('正确', '错误') else
                    '答案引用了缺失选项' if row['qtype'] in TYPES[:2] and
                    any(key not in row['options'] for key in row['answer']) else '')
    return row


def question(qid):
    row = query('SELECT * FROM questions WHERE id=?', (qid,), one=True)
    return unpack(row) if row else None


def parse_question(data, complete=True):
    row = {key: str(data.get(key, '') or '').strip() for key in FIELDS if key != 'options'}
    if not row['id'] or (complete and (not row['stem'] or not row['answer'])):
        raise ValueError('题号、题干和答案不能为空。')
    if row['qtype'] not in TYPES:
        raise ValueError('请选择单选、多选、判断或填空题。')
    options = {key: data.get(key, '').strip() for key in LETTERS if data.get(key, '').strip()}
    row['answer'] = normalize_answer(row['answer'], row['qtype'])
    if complete and row['qtype'] in TYPES[:2]:
        if len(options) < 2 or not row['answer'] or any(key not in options for key in row['answer']):
            raise ValueError('选择题至少需要两个选项，答案只能包含已有选项的字母。')
        if row['qtype'] == '单选题' and len(row['answer']) != 1:
            raise ValueError('单选题只能设置一个答案。')
    elif complete and row['qtype'] == '判断题' and row['answer'] not in ('正确', '错误'):
        raise ValueError('判断题答案请填写“正确”或“错误”。')
    if row['qtype'] not in TYPES[:2]:
        options = {}
    row['options'] = json.dumps(options, ensure_ascii=False)
    row['category'] = row['category'] or '未分类'
    row['difficulty'] = row['difficulty'] or '无'
    return row


def import_csv(content):
    reader = csv.DictReader(io.StringIO(content.lstrip('\ufeff'), newline=''), strict=True)
    try:
        if not {'题号', '题干', '答案', '题型'} <= set(reader.fieldnames or []):
            raise ValueError('CSV 必须包含：题号、题干、答案、题型。')
        sources = list(reader)
    except csv.Error as error:
        raise ValueError(f'第 {reader.line_num} 行 CSV 格式错误：{error}') from error
    rows, seen = [], set()
    for line, source in enumerate(sources, 2):
        if None in source or any(value is None for value in source.values()):
            raise ValueError(f'第 {line} 行：列数与表头不一致。')
        if not any(source.values()):
            continue
        try:
            row = parse_question(dict(zip(FIELDS, [source.get(key, '') for key in
                ('题号', '题干', '答案', '难度', '题型', '类别', 'options', '解析')])) | {
                key: source.get(key, '') or '' for key in LETTERS}, complete=False)
            if row['id'] in seen:
                raise ValueError(f'题号 {row["id"]} 在文件中重复。')
        except ValueError as error:
            raise ValueError(f'第 {line} 行：{error}') from error
        seen.add(row['id'])
        rows.append(row)
    if not rows:
        raise ValueError('文件中没有题目。')
    existing = {row['id'] for row in query('SELECT id FROM questions')}
    updated = len(seen & existing)
    with get_db() as conn:
        conn.executemany(UPSERT, [tuple(row[key] for key in FIELDS) for row in rows])
    return len(rows) - updated, updated


def export_csv(rows):
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for source in rows:
        row = unpack(source)
        writer.writerow(dict(zip(['题号', '题干', '答案', '难度', '题型', '类别', '解析'],
                                 [row[key] for key in FIELDS if key != 'options'])) | {
            key: row['options'].get(key, '') for key in LETTERS})
    return output.getvalue().encode('utf-8-sig')


def grade(row, values):
    answer = normalize_answer(''.join(values), row['qtype'])
    return answer, int(bool(answer) and answer == normalize_answer(row['answer'], row['qtype']))
