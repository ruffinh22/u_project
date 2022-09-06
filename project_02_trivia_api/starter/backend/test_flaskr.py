import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db_user, db_pass, db_host, datab_test


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql+psycopg2://{}:{}@{}/{}".format(self.db_user, self.db_pass, self.db_host, self.datab_test) 
        setup_db(self.app, self.database_path)

        self.new_question={
            "question":"what country is to the east of Benin ?",
            "answer": "Nigeria",
            "category": 4,
            "difficulty": 2}

        self.existant_question={
           "question":"Who invented Peanut Butter?",
            "answer": "George Washington Carver",
            "category": 3,
            "difficulty": 2}

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
    def test_retrieve_categories(self):
        '''  test to show categories '''
        res = self.client().get('/categories')
        data = res.get_json()
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']))

    def test_get_paginate_questions(self):
        ''' test for successful retrival of questions in page 1'''
        res = self.client().get('/questions?page=2')
        data = res.get_json()
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(len(data['questions']))

    def test_404_sent_requesting_beyond_valid_page(self):
        ''' test for failure of retrival of questions in not found page'''
        res = self.client().get('/questions?page=1000')
        data = res.get_json()
        self.assertEqual(res.status_code,404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'],'resource not found')
    
    def test_delete_question_success(self):
        ''' test for successful deletion of a question'''
        res = self.client().delete('/question/18')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'],18)
        

    def test_404_delete__if_question_no_exist(self):
        ''' test for failure deletion on non_existant question'''
        res = self.client().delete('/questions/2000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'],'resource not found')


    def test_create_new_question_successful(self):
        ''' test successfull addition of new question'''
        res = self.client().post('/questions',json = self.new_question)
        data = json.loads(res.data)   
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'], True)

    def test_404_create_new_question_successful(self):
        ''' test no successfull addition of new question'''
        res = self.client().post('/questions',json = self.existant_question)
        data = json.loads(res.data)   
        self.assertEqual(res.status_code,500)
        self.assertFalse(data['success'], False)
        self.assertEqual(data['message'],'resource already exists')
        

    def test_search_term_successful(self):
        ''' test of successful search for specific question'''
        res = self.client().post('/questions/search?search=whose')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
     
    def test_search_term_no_successful(self):
        ''' test of successful search for specific question'''
        res = self.client().post('/questions/search?search=whosemmmf')
        data = res.get_json()
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data["message"], "resource not found")


    def test_retrieve_questions_in_specific_category(self):
        ''' test of retreival of questions on specific category'''
        res = self.client().get('/categories/3/questions')
        data = res.get_json()
        self.assertEqual(res.status_code,200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['success'])
    
    def test_retrieve_questions_in_non_existant_category(self):
        ''' test for retreival questions in non existant category'''
        res = self.client().get('/categories/111/questions')
        data = res.get_json()
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['message'],"resource not found")
        self.assertFalse(data['success'])

    def test_play_quiz_questions(self):
        """Tests playing quiz questions"""

        # mock request data
        request_data = {
            'previous_questions': [5, 9, 12],
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
        self.assertNotEqual(data['question']['id'], 12
        )
        # Ensures returned question is in the correct category
        self.assertEqual(data['question']['category'], 4)

    def test_no_data_to_play_quiz(self):
        """Test for the case where no data is sent"""

        # process response from request without sending data
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "bad request")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()