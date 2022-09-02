from json import load
import os
import string
from unicodedata import category
from unittest import result
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.orm import load_only

from sqlalchemy import select

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page -1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [quest.format() for quest in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    

    """
    @TODO[DONE]: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    
    CORS(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    
    # CORS Headers
    
    """
    @TODO[DONE]: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        response.headers.add(
            "Access-Control-Allow-Origin", "*"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
    # http://127.0.0.1:5000/categories

        categories = db.session.query(Category).order_by(Category.id).all()
    
        if len(categories) == 0:
            abort(404)

        return jsonify ({
            'success': True,
            'categories': {item.id: item.type for item in categories}
        })
        

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
    # http://127.0.0.1:5000/questions?page=2

        # selection = db.session.query(Question).order_by(Question.id)
        selection = db.session.query(Question).options(load_only
        (Question.question, Question.category)).order_by(Question.id)
        # selection = Question.query.with_entities(Question.question, Question.category)
        # selection = Question.query.options(load_only(Question.category)).all()
        # selection = db.session.query(Question.question, Question.category)
        categories = Category.query.all()
        question = Question.query.all()
        # return selection
        questions = paginate_questions(request, selection)

        if len(questions) == 0:
            abort(404)

        return jsonify({
                "success": True,
                "questions": list(questions),
                "total_questions": len(question),
                "current_category": None,
                #"categories": {category.id: category.type for category in categories
                "total_categories": {item.id: item.type for item in categories}
            })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            # del_question = Question.query(Question.question).filter(Question.id == question_id)
            
            if question is None:
                abort(404)
            
            question.delete()

            tot_question = len(Question.query.all())

            return jsonify({
                'success': True,
                'deleted': question_id,
                # 'question_deleted': del_question,
                'total_questions': tot_question
            })
        except:
            abort(422)
      
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_question():

        body = request.get_json()

        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')

        if (body, new_question, new_answer, new_category, new_difficulty) == None:
            abort(422)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
                )

            question.insert()

            tot_questions = Question.query.all()
            current_questions = paginate_questions(request, tot_questions)

            return jsonify({
            'success': True,
            #'created': question.id,
            #'questions': current_questions,
            # 'created': question.new_question,
            'total_questions': len(tot_questions)
        })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods = ['POST'])
    # http://127.0.0.1:5000/questions/search?search=What

    def search_questions():

        search_term = request.args.get('search' , None)

     

        selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        
        # question = Question.query.all()

        if len(selection) == 0 or search_term == '':
            abort(404)

      

        else:
            current_questions = paginate_questions(request, selection)

            return jsonify({
            'success': True,
            'questions': [sel.format() for sel in selection],
            'total_questions': len(selection),
        })


    """
    @TODO:
    Create a GET endpoint to get questions based on category.
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def category_questions(category_id):
    # http://127.0.0.1:5000/category/2/questions

        try:
            selection = Question.query.filter(category_id == Question.category).all()
    
            current_questions = paginate_questions(request, selection)
            categories = Category.query.all()

            if category_id > len(categories):
                abort(404)

            return jsonify({
                    "success": True,
                    "questions": list(current_questions),
                    "total_questions": len(selection),
                    
                   # "current_category": [my_str.join(cat.type) if cat.id == category_id else 'x' for cat in categories]
                    "current_category": [cat.type for cat in categories if cat.id == category_id ]
                })
        except:
            abort(404)
        

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz_question():
        """This returns a random question to play quiz."""

        # process the request data and get the values
        data = request.get_json()
        previous_questions = data.get('previous_questions')
        quiz_category = data.get('quiz_category')

        # return 404 if quiz_category or previous_questions is empty
        if ((quiz_category is None) or (previous_questions is None)):
            abort(404)

        # if default value of category is given return all questions
        # else return questions filtered by category
        if (quiz_category['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(
                category=quiz_category['id']).all()

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


  

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return( 
            jsonify({'success': False, 'error': 404,'message': 'resource not found'}),
            404
        )
    
    @app.errorhandler(422)
    def unprocessed(error):
        return(
            jsonify({'success': False, 'error': 422,'message': 'request cannot be processed'}),
            422

        )

    @app.errorhandler(400)
    def bad_request(error):
        return(
            jsonify({'success': False, 'error': 400,'message': 'bad request'}),
            400

        )

    @app.errorhandler(405)
    def not_allowed(error):
        return(
            jsonify({'success': False, 'error': 405,'message': 'method not alllowed'}),
            405

        )
        


    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)