from flask_sqlalchemy import SQLAlchemy
import os
import unittest
import json
from flaskr import create_app
from models import setup_db, Question, Category
from flask_migrate import Migrate

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}@{}/{}".format('postgres', 'localhost:5432', "trivia_test")
        setup_db(self.app, self.database_path)



        self.new_question={
            'question':"ggg hhhxxxzzz hhh",
            'answer': "ggg",
            'category':2,
            'difficulty': 3
        }
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
    '''
    test 1 testing getting all questions successfully
    '''
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions']) 


    '''
    test 2 testing getting all questions with error
    '''    

    def test_get_paginated_questions_error_404(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')    

    '''
    test 3 testing getting all categories with success
    ''' 
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(res.status_code, 200)


    '''
    test 4 testing posting question  with success
    '''

    def test_post_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        question=Question.query.filter(Question.question.ilike('%hhhxxxzzz%')).order_by(Question.id).all()
        self.assertTrue(question)
        self.assertEqual(res.status_code, 200)
    '''
    test 5 testing posting question with error
    '''  
    def test_422_post_failure_question(self):
        res = self.client().post('/questions', json={
            'question':"ggg hhhxxxzzz hhh",
            'answer': "ggg",
            'category':2,
        })
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 422)
    '''
    test 6 testing deleting question with success
    '''  
    def test_delete_question(self):
        question=Question.query.all()
        question_id=question[0].id
        res = self.client().delete('/questions/'+str(question_id))
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        question=Question.query.filter(Question.id == question_id).one_or_none()
        self.assertEqual(question, None)   
        self.assertEqual(res.status_code, 200)  
    '''
    test 7 testing deleting question with error
    '''  
    def test_delete_failed_404_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)   
        self.assertEqual(res.status_code,404)  

    '''
    test 8 testing getting questions by category  with success
    '''  
    def test_get_categor_byId(self):
        res = self.client().get('/categories/0/questions')
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['currentCategory'], 'Science')
        self.assertEqual(res.status_code, 200)    
        self.assertTrue(data['totalQuestions'])
    '''
    test 9 testing getting questions by category  with error
    '''  
    def test_get_error404_categor_byId(self):
        res = self.client().get('/categories/7/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404) 
        self.assertEqual(data['success'], False)
    '''
    test 10 testing getting quiz questions by category  with sucess
    '''      
    def test_getQuizQuestion(self):
        res = self.client().post('/quizzes', json={"quiz_category":{'type': 'Science', 'id': '0'},"previous_questions":[]})
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(res.status_code, 200)  
    '''
    test 11 testing getting quiz questions by category  with error
    '''      
    def test_error404_getQuizQuestion(self):
        res = self.client().post('/quizzes', json={"quiz_category":{'type': 'Science', 'id': '8'},"previous_questions":[]})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code,404)
    '''
    test 12 testing  search for  questions by string in case insensitive matter
    ''' 
    def test_search_questions(self):
        res = self.client().post('/questions/search', json={'searchTerm':'hhhxxxzzz'})
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code,200)     
        self.assertTrue(data['questions'])  
        self.assertTrue(data['totalQuestions']) 

    '''
    test 13 testing error search for  questions by string ,without providing search parameter
    ''' 
    def test_search_questions_error404(self):
        res = self.client().post('/questions/search',json={"gehe":"jeek"})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code,422)     


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()