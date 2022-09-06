import os
import sys
from flask import Flask, request, abort, jsonify, flash,json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category,db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    categories = Category.query.order_by(Category.type).all()
    if len(categories) == 0:
      abort(404)
    return jsonify({
        'success': True,
        'categories': {category.id: category.type for category in categories}
        })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    categories = Category.query.order_by(Category.type).all()
    #cur =json.dumps(Category.query.order_by(Category.type).first())
    if len(current_questions) == 0:
      abort(404)

    
    return jsonify({
      'success': True,
      'questions': current_questions,
      'totalQuestions': len(selection),
      'categories': {category.id: category.type for category in categories},
      'curruntCategory': None
       })
    
       
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions/<int:question_id>", methods=['DELETE'])
  def delete_question(question_id):
    try:
      question= Question.query.get(question_id)
      db.session.delete(question)
      db.session.commit()
      return jsonify({
        'success': True,
        'deleted': question_id
        })
    except:
      abort(404)
     
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route("/questions", methods=['POST'])
  def create_new_question():
    #data=Question()
    body = request.get_json()
    
    new_question = body.get('question')
    new_answer = body.get('answer')
    new_difficulty = body.get('difficulty')
    new_category = body.get('category')
    
    selection = Question.query.filter(Question.question==new_question).all()
    if selection:
        abort(500)
    else:
      try:
        question = Question(question=new_question, answer=new_answer,  difficulty=new_difficulty, category=new_category)
        question.insert()
        return jsonify({

          'success': True,
            })
      except:
        abort(422)
        
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    
    search_term = request.args.get('search','' )
    selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    #data=search_questions()
    #data = json.loads(request.data) 
    
    if len(selection) == 0:
      abort(404)
    else:
      search_questions = paginate_questions(request, selection)
    
    
      return jsonify({
      'success': True,
      'questions': [req.format() for req in selection],
      'totalQuestions': len(selection)
      #'currentCategory':  None
        })

    
    # http://127.0.0.1:5000/questions/search?search=Whose
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def retrieve_questions_by_category(category_id):
     # http://127.0.0.1:5000/category/5/questions
    try:
      current_category_id= Category.query.get(category_id)
      questions = Question.query.filter(Question.category == str(category_id)).all()
      if (current_category_id is None):
        abort(400)
      else:
        return jsonify({
        'success': True,
        'questions': [question.format() for question in questions],
        'totalQuestions': len(questions),
        'currentCategory': current_category_id.type
        })
    except:
      abort(404)

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
  @app.route('/quizzes', methods=['POST'])
  def play_quiz_question():

        """This returns a random question to play quiz."""

        # process the request data and get the values
        data = request.get_json()
        previous_questions = data.get('previous_questions')
        quiz_category = data.get('quiz_category')

        # return 404 if quiz_category or previous_questions is empty
        if ((quiz_category is None) or (previous_questions is None)):
            abort(400)

        # if default value of category is given return all questions
        # else return questions filtered by category
        if (quiz_category['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by( category=quiz_category['id']).all()

        # defines a random question generator method
        def get_random_question():
          return questions[random.randint(0, len(questions)-1)]

        # get random question for the next question
        next_question = get_random_question()

        # defines boolean used to check that the question
        # is not a previous question
        found = True

        while found:
            if next_question.id in previous_questions:
                next_question = get_random_question()
            else:
                found = False
        return jsonify({
            'success': True,
            'question': next_question.format(),
        }), 200

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  @app.errorhandler(404)
  def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

  @app.errorhandler(422)
  def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

  @app.errorhandler(400)
  def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

  @app.errorhandler(405)
  def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

  @app.errorhandler(500)
  def ressource_already(error):
        return (
            jsonify({"success": False, "error": 500, "message": "resource already exists"}),
            500,
        )
  return app