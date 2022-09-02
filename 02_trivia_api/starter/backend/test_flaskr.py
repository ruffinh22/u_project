import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "lidruf", "janvier22", "localhost:5432", self.database_name
       )
        setup_db(self.app, self.database_path)

        self.new_question = {"question":"what is my name", "answer":"Stephen Nwankwo", "category":"5", "difficulty":"2"}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

# ------------------------------------------------------------------------------
#  TEST FOR ALL QUESTION RELATED QUERIES 
# ------------------------------------------------------------------------------

    def test_get_questions_by_page(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertFalse(data['current_category'])
        self.assertTrue(data['total_categories'])

    def test_404_request_beyond_valid_pages(self):
        res = self.client().get('/questions?page=2000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_delete_question(self):
        res = self.client().delete('/questions/17')
        data = json.loads(res.data)

        #question = Question.query.filter(Question.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 17)
        self.assertTrue(data['total_questions'])
        #self.assertTrue(data['question_deleted'])
        #self.assertEqual(question, None)

    def test_422_question_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'request cannot be processed')

    def test_add_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
    




    def test_get_question_search_with_results(self):
        res = self.client().post('/questions/search?search=what')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
       # self.assertTrue(data['total_questions'])

    def test_404_get_search_unavailable_question(self):
        res = self.client().post('/questions/search', json={"search": "ghygthyhujhhg"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        #self.assertEqual(data['questions'], 0)
        # self.assertEqual(data['total_questions'], 0)

    



# ------------------------------------------------------------------------------
#  TEST FOR ALL CATEGORY SPECIFIC QUERIES 
# ------------------------------------------------------------------------------

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_question_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_get_question_beyond_valid_categories(self):
        res = self.client().get('/categories/69/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_play_quiz_questions(self):
        """Tests playing quiz questions"""

        # mock request data
        request_data = {
            'previous_questions': [5, 9],
            'quiz_category': {
                'type': 'History',
                'id': 4
            }
        }

        # make request and process response
        response = self.client().post('/quizzes', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        # Ensures previous questions are not returned
        self.assertNotEqual(data['question']['id'], 5)
        self.assertNotEqual(data['question']['id'], 9)

        # Ensures returned question is in the correct category
        self.assertEqual(data['question']['category'], 4)

    def test_play_quiz_with_invalid_category(self):
        res = self.client().post('/quizzes', json={"quiz_category": {"id    ": "69"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


# ------------------------------------------------------------------------------
#



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()