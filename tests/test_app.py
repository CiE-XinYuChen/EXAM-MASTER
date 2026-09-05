import csv
from contextlib import closing
import io
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as bootstrap:
    os.chdir(bootstrap)
    os.environ["EXAM_DATABASE"] = str(Path(bootstrap) / "database.db")
    os.environ["EXAM_SEED_CSV"] = ""
    import app as web
    os.environ.pop("EXAM_DATABASE")
    os.environ.pop("EXAM_SEED_CSV")
    os.chdir(ROOT)


class WebTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        os.chdir(self.temp.name)
        self.database = str(Path(self.temp.name) / 'database.db')
        web.app.config.update(TESTING=True, DATABASE=self.database, SEED_CSV=None)
        with web.app.app_context():
            web.init_db()
        self.client = web.app.test_client()
        self.client.post('/register', data={'username': 'learner', 'password': 'practice123',
                                          'confirm_password': 'practice123'})
        self.client.post('/login', data={'username': 'learner', 'password': 'practice123'})
        with closing(sqlite3.connect(self.database)) as conn, conn:
            conn.executemany('INSERT INTO questions (id,stem,answer,qtype,category,difficulty,options) VALUES (?,?,?,?,?,?,?)', [
                ('1', '单选示例', 'A', '单选题', '基础', '简单', '{"A":"一","B":"二"}'),
                ('2', '多选示例', 'AB', '多选题', '基础', '中等', '{"A":"甲","B":"乙","C":"丙"}'),
                ('3', '文字填空', '北京', '填空题', '地理', '简单', '{}'),
                ('4', '判断示例', '正确', '判断题', '地理', '简单', '{}'),
            ])

    def tearDown(self):
        os.chdir(ROOT)
        self.temp.cleanup()

    def rows(self, sql, params=()):
        with closing(sqlite3.connect(self.database)) as conn, conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(sql, params)]

    def csv_upload(self, content):
        return self.client.post('/questions/import', data={
            'file': (io.BytesIO(content.encode('utf-8-sig')), 'questions.csv')}, follow_redirects=True)

    def test_question_create_edit_delete(self):
        form = dict(id='new-1', stem='新增题目', answer='A', qtype='单选题', A='正确选项', B='另一选项',
                    category='新分类', difficulty='简单', explanation='解析内容')
        response = self.client.post('/questions/new', data=form)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.rows('SELECT explanation FROM questions WHERE id=?', ('new-1',)),
                         [{'explanation': '解析内容'}])
        form.update(stem='已编辑题目', answer='B')
        self.client.post('/questions/new-1/edit', data=form)
        self.assertEqual(self.rows('SELECT stem,answer FROM questions WHERE id=?', ('new-1',)),
                         [{'stem': '已编辑题目', 'answer': 'B'}])
        self.client.post('/favorite/new-1')
        self.client.post('/questions/new-1/delete')
        self.assertEqual(self.rows('SELECT id FROM questions WHERE id=?', ('new-1',)), [])
        self.assertEqual(self.rows('SELECT * FROM favorites WHERE question_id=?', ('new-1',)), [])

    def test_duplicate_id_does_not_overwrite_question(self):
        response = self.client.post('/questions/new', data=dict(id='1', stem='重复', qtype='填空题', answer='答案'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.rows('SELECT stem FROM questions WHERE id="1"')[0]['stem'], '单选示例')

    def test_csv_import_upserts_and_round_trips_unicode(self):
        response = self.csv_upload('题号,题干,A,B,C,D,E,答案,难度,题型,类别,解析\n1,更新题目,一,二,,,,B,简单,单选题,中文分类,说明\n9,城市,,,,,,北京,中等,填空题,地理,首都\n')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.rows('SELECT stem,answer FROM questions WHERE id="1"'),
                         [{'stem': '更新题目', 'answer': 'B'}])
        exported = self.client.get('/questions/export?category=地理')
        self.assertEqual(exported.status_code, 200)
        records = list(csv.DictReader(io.StringIO(exported.data.decode('utf-8-sig'))))
        self.assertEqual({r['题号'] for r in records}, {'3', '4', '9'})
        self.assertEqual(next(r for r in records if r['题号'] == '9')['解析'], '首都')
        self.assertEqual(self.csv_upload(exported.data.decode('utf-8-sig')).status_code, 200)
        self.assertEqual(len(self.rows('SELECT id FROM questions')), 5)

    def test_bad_csv_rolls_back_the_whole_file(self):
        response = self.csv_upload('题号,题干,答案,题型\n8,有效题目,北京,填空题\n,缺少题号,上海,填空题\n')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.rows('SELECT id FROM questions WHERE id IN ("8","9")'), [])

    def test_malformed_csv_does_not_partially_import(self):
        self.assertEqual(self.csv_upload('"题号,题干,答案,题型\n8,题目,北京,填空题').status_code, 400)
        for bad_row in ['9,多了一列,上海,填空题,意外内容', '9,少了一列,上海', '9,"未闭合的引号,上海,填空题']:
            with self.subTest(row=bad_row):
                response = self.csv_upload('题号,题干,答案,题型\n8,有效题目,北京,填空题\n' + bad_row)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(self.rows('SELECT id FROM questions WHERE id IN ("8","9")'), [])

    def test_search_combines_filters_and_handles_out_of_range_page(self):
        response = self.client.get('/questions?search=示例&category=基础&type=多选题&page=999')
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn('多选示例', body)
        self.assertNotIn('单选示例', body)

    def test_all_four_question_types_grade_correctly(self):
        for qid, answer in [('1', 'A'), ('2', ['B', 'A']), ('3', '北京'), ('4', '正确')]:
            response = self.client.post('/question/' + qid, data={'answer': answer}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
        self.assertEqual([row['correct'] for row in self.rows('SELECT correct FROM history ORDER BY id')], [1, 1, 1, 1])

    def test_fill_blank_does_not_sort_characters(self):
        self.client.post('/question/3', data={'answer': '京北'})
        self.assertEqual(self.rows('SELECT user_answer,correct FROM history'), [{'user_answer': '京北', 'correct': 0}])

    def test_sequential_resume_is_not_changed_by_random_browsing(self):
        self.client.post('/sequential/1', data={'answer': 'A'})
        self.client.get('/question/4')
        response = self.client.get('/sequential_start')
        self.assertIn('/2', response.location)

    def test_favorites_tags_and_wrong_questions(self):
        self.client.post('/favorite/1')
        self.client.post('/update_tag/1', data={'tag': '考前复习'})
        self.assertEqual(self.rows('SELECT tag FROM favorites'), [{'tag': '考前复习'}])
        self.assertIn('单选示例', self.client.get('/favorites').get_data(as_text=True))
        self.client.post('/question/1', data={'answer': 'B'})
        self.assertIn('单选示例', self.client.get('/wrong').get_data(as_text=True))
        self.client.post('/unfavorite/1')
        self.assertEqual(self.rows('SELECT * FROM favorites'), [])

    def test_learning_records_are_separate_for_each_user(self):
        self.client.post('/question/1', data={'answer': 'A'})
        self.client.get('/logout')
        self.client.post('/register', data={'username': 'another', 'password': 'practice123',
                                           'confirm_password': 'practice123'})
        self.client.post('/login', data={'username': 'another', 'password': 'practice123'})
        self.assertNotIn('单选示例', self.client.get('/history').get_data(as_text=True))

    def test_exam_result_persists_and_resubmission_does_not_duplicate_history(self):
        response = self.client.post('/start_exam', data={'question_count': '4'})
        self.assertEqual(response.status_code, 302)
        exam_id = self.rows('SELECT id FROM exam_sessions')[0]['id']
        answers = {'answer_1': 'A', 'answer_2': ['B', 'A'], 'answer_3': '北京', 'answer_4': '正确'}
        result = self.client.post(f'/exam/{exam_id}', data=answers, follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(self.rows('SELECT completed,score FROM exam_sessions'), [{'completed': 1, 'score': 100.0}])
        self.client.post(f'/exam/{exam_id}', data=answers)
        self.assertEqual(len(self.rows('SELECT id FROM history')), 4)
        self.assertIn('100', self.client.get(f'/exam/{exam_id}').get_data(as_text=True))

    def test_exam_uses_snapshot_if_question_is_edited(self):
        self.client.post('/start_exam', data={'question_count': '4'})
        exam_id = self.rows('SELECT id FROM exam_sessions')[0]['id']
        with closing(sqlite3.connect(self.database)) as conn, conn:
            conn.execute('UPDATE questions SET answer="B" WHERE id="1"')
        self.client.post(f'/exam/{exam_id}', data={'answer_1': 'A'})
        self.assertEqual(self.rows('SELECT correct FROM history WHERE question_id="1"'), [{'correct': 1}])

    def test_empty_bank_does_not_start_an_empty_exam(self):
        with closing(sqlite3.connect(self.database)) as conn, conn:
            conn.execute('DELETE FROM questions')
        response = self.client.post('/start_exam', data={'question_count': '10'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.rows('SELECT id FROM exam_sessions'), [])

    def test_incomplete_legacy_questions_are_skipped_in_exams(self):
        with closing(sqlite3.connect(self.database)) as conn, conn:
            conn.execute('UPDATE questions SET stem="" WHERE id="1"')
        self.client.post('/start_exam', data={'question_count': '4'})
        paper = json.loads(self.rows('SELECT paper FROM exam_sessions')[0]['paper'])
        self.assertEqual({row['id'] for row in paper}, {'2', '3', '4'})

    def test_original_bank_round_trip_keeps_incomplete_questions(self):
        response = self.csv_upload((ROOT / 'questions.csv').read_text(encoding='utf-8-sig'))
        self.assertEqual(response.status_code, 200)
        exported = self.client.get('/questions/export')
        self.assertEqual(self.csv_upload(exported.data.decode('utf-8-sig')).status_code, 200)
        self.assertEqual(len(self.rows('SELECT id FROM questions')), 881)
        self.assertEqual(len(self.rows('SELECT id FROM questions WHERE stem=""')), 18)

    def test_filtered_sequential_practice_keeps_the_filter_after_answering(self):
        self.client.get('/practice/sequential?category=地理', follow_redirects=True)
        response = self.client.post('/question/3?mode=sequential&category=地理', data={'answer': '北京'})
        self.assertIn('category=', response.location)
        result = self.client.get(response.location)
        self.assertIn('/question/4?', result.get_data(as_text=True))
        self.client.post('/question/4?mode=sequential&category=地理', data={'answer': '正确'}, follow_redirects=True)
        with self.client.session_transaction() as session:
            uid = session['user_id']
        self.assertEqual(self.rows('SELECT current_seq_qid FROM users WHERE id=?', (uid,))[0]['current_seq_qid'], '3')

    def test_question_id_with_a_slash_can_be_opened_and_edited(self):
        self.client.post('/questions/new', data=dict(id='unit/1', stem='章节题目', qtype='填空题', answer='答案'))
        self.assertEqual(self.client.get('/question/unit/1').status_code, 200)
        self.assertEqual(self.client.get('/questions/unit/1/edit').status_code, 200)

    def test_deleted_question_id_is_not_reused_for_new_content(self):
        self.client.post('/question/4', data={'answer': '正确'})
        self.client.post('/questions/4/delete')
        page = self.client.get('/questions/new').get_data(as_text=True)
        self.assertIn('name="id" value="5"', page)
        response = self.client.post('/questions/new', data=dict(id='4', stem='另一道题', qtype='填空题', answer='答案'))
        self.assertEqual(response.status_code, 400)

    def test_legacy_database_upgrade_preserves_learning_records(self):
        self.client.post('/favorite/1')
        self.client.post('/question/1', data={'answer': 'A'})
        with closing(sqlite3.connect(self.database)) as conn, conn:
            conn.execute('ALTER TABLE questions DROP COLUMN explanation')
            conn.execute('ALTER TABLE exam_sessions DROP COLUMN paper')
            conn.execute('UPDATE users SET current_seq_qid="2"')
            conn.execute('INSERT INTO exam_sessions (user_id,mode,question_ids,start_time,duration,completed,score) '
                         'VALUES (1,"exam",\'["1","2"]\',"2025-05-01 12:00:00.123456",0,1,50)')
        with web.app.app_context():
            web.init_db()
        self.assertEqual(len(self.rows('SELECT * FROM history')), 1)
        self.assertEqual(len(self.rows('SELECT * FROM favorites')), 1)
        self.assertEqual(self.rows('SELECT current_seq_qid FROM users')[0]['current_seq_qid'], '2')
        self.assertEqual(self.client.get('/exam/1').status_code, 200)
        self.assertIn('50', self.client.get('/exam/1').get_data(as_text=True))

    def test_reset_clears_only_current_user_learning_state(self):
        self.client.post('/question/1', data={'answer': 'A'})
        self.client.post('/reset_history')
        self.assertEqual(self.rows('SELECT id FROM history'), [])
        self.assertIsNone(self.rows('SELECT current_seq_qid FROM users')[0]['current_seq_qid'])


if __name__ == '__main__':
    unittest.main()
