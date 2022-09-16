import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
#from flask_restful import Resource
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth



app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()


# ROUTES
'''
Implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks or appropriate status code
    indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        })

    except Exception:
        abort(404)


'''
Implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks or appropriate
    status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(token):
    try:
        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        })

    except Exception:
        abort(404)


'''
Implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    body = request.get_json()
    if not ('title' in body and 'recipe' in body):
        abort(422)

    new_drink = body.get('title')
    new_recipe = body.get('recipe')

    try:
        drink = Drink(title=new_drink, recipe=json.dumps(new_recipe))
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })

    except Exception:
        abort(404)


'''
Implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''





@app.route('/drinks/<int:drinks_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks(payload, drinks_id):
    drink = Drink.query.filter(Drink.id == drinks_id).one_or_none()
    if drink is None:
        abort(404)
    body = request.get_json()
    json_body = request.get_json()
    req_title = body.get('title')
    recipe = json_body.get('recipe', None)
    #req_recipe = json.dumps(body['recipe'])
    try:
        drink.title = req_title
        drink.recipe = recipe if type(body.get('recipe')) == str else json.dumps(body.get('recipe'))
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]

        })
    except Exception as e:
        print(e)
        abort(422)


'''
Implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id
    is the id of the deleted record or appropriate status code indicating
    reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    daDrink = Drink.query.get(id)

    if daDrink:
        try:

            daDrink.delete()

            return jsonify({
                "success": True,
                "delete": id
            })

        except Exception:
            abort(422)
    else:
        abort(404)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
Implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''

'''
Implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
Implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    return jsonify({
        "success": False,
        "error": ex.status_code,
        'message': ex.error
    }), 401


'''
Implement error handler for 400
    error handler should conform to general task above
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


'''
Implement error handler for 500 internal server error
    error handler should conform to general task above
'''


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500
