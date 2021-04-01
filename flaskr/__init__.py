import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from dotenv import load_dotenv 
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
load_dotenv()

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response  
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    selection=Category.query.all()
    if len(selection) == 0:
      abort(404)
    cats = [category.format()['category'] for category in selection]
    return jsonify({
      "success":True,
      "categories":cats
    })


  
  @app.route('/questions',methods=["GET","POST"])
  def retrieve_questions():
    if request.method=="GET":
      # print(request.method)
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)
      current_categories=Category.query.order_by(Category.id).all()
      cats = [category.format()['category'] for category in current_categories]
      if len(current_questions) == 0:
        abort(404)
      return jsonify({
        'success': True,
        'questions': current_questions,
        'totalQuestions': len(Question.query.all()),
        'categories':cats,
      })  
    elif request.method=="POST":
      # print(request.method)
      body=request.get_json()
      question_body=body.get('question',None)
      question_answer=body.get('answer',None)
      question_category=body.get('category',None)
      question_diff=body.get('difficulty',None)

      if question_body is None or question_answer is None or question_category is None or question_diff is None:
        abort(422)
      try:
        question=Question(question=question_body,answer=question_answer,difficulty=question_diff,category=question_category)
        question.insert()
      except:
        db.session.rollback()
        abort(500)
      return jsonify({"success":True})

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_questions(question_id):
    question=Question.query.get(question_id)
    if question is None:
      abort(404) 
    try:
      question.delete()   
    except:
      db.session.rollback()
      abort(422)
    return jsonify({
      "success":True
    })
   
  '''

  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search',methods=['POST'])
  def search_questions():
    body=request.get_json()
    # print(body)
    search_term=body.get('searchTerm',None)
    if search_term is None:
      abort(422)
    questions=Question.query.filter(Question.question.ilike('%'+search_term+'%')).order_by(Question.id).all()
    # print(questions)
    if questions is not None:
      questions=[question.format() for question in questions]
    return jsonify({
    "success":True,
    "questions": questions,
    "totalQuestions":len(Question.query.all())
    })


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions',methods=['GET'])
  def get_cat_questions(category_id):
    if category_id >5:
      abort(404)
    selection=Question.query.filter(Question.category==category_id).all()
    selection=[quest.format() for  quest in selection]
    current_category=Category.query.get(category_id).type
    return jsonify({
      "questions": selection,
      "currentCategory": current_category,
      "totalQuestions": len(Question.query.all()),
      "success":True
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def get_quiz_questions():
    body=request.get_json()
    previous_questions=body.get("previous_questions",None)
    cat=body.get("quiz_category",None)
    # print(cat)
    if cat['type']=='click':
        questions=Question.query.all()
    else:
        questions=Question.query.filter(Question.category==cat['id']).all()
    if questions ==[]:
      abort(404)
    questions=[quest.format() for  quest in questions]
    cat_all_IDs=[]
    previous_IDS=[]
    for quest in questions:
      cat_all_IDs.append(quest['id'])
    # print(previous_questions)
    for ques in previous_questions:
      previous_IDS.append(ques)

    # print("all IDS: ")
    print(cat_all_IDs)
    # print("previous IDS: ")
    # print(previous_IDS)

    for ID in previous_IDS:
      cat_all_IDs.remove(ID)
    # print("new all IDS: ")
    # print(cat_all_IDs)
    questions_number=len(cat_all_IDs)
    if questions_number:
      currentQuestion=Question.query.get(cat_all_IDs[random.randint(0,questions_number-1)]).format()
    else:
      currentQuestion=None
    # print("returned questions")
    # print(currentQuestion)
    return jsonify({
      "question":currentQuestion,
      "success":True
    })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400  

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422


  
  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "server error"
      }), 500
  return app

    