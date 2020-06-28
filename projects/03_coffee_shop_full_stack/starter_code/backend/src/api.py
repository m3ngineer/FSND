import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(user):

    try:
        if ('get:drinks-detail' in user['permissions']):
            drinks = Drink.query.all()
            drinks = [drink.long() for drink in drinks]

            return jsonify({
                    "success": True,
                    "drinks": drinks
                }), 200
        else:
            abort(403)
    except Exception as error:
        raise error

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['post'])
@requires_auth('post:drinks')
def create_drink(jwt):

    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        drink = Drink(title=title , recipe=json.dumps(recipe))
        drink.insert()

        return jsonify ({
            "success": True ,
            "drinks": drink.long(),
          }), 200

    except Exception as error:
        raise error

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['patch'])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):

    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if not drink:
            abort(404)

        body = request.get_json()

        title = body.get('title', None)
        recipe = body.get('recipe', [])

        if title == '':
            abort(400)

        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()

        return jsonify ({
            "success": True ,
            "drinks": drink.long(),
          }), 200

    except Exception as error:
        raise error

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def remove_drink(jwt, drink_id):

    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if not drink:
            abort(404)

        drink.delete()

        return jsonify({"success": True, "delete": drink_id}), 200

    except Exception as error:
        raise error


## Error Handling
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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "Resource not found"
                    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def authentification_error(error):
    return jsonify({
                    "success": False,
                    "error": error.error,
                    "message": "Authentification error"
                    }), error.status_code

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
                    "success": False,
                    "error": 403,
                    "message": "Forbidden"
                    }), 403

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "Bad request"
                    }), 400

@app.errorhandler(405)
def unallowed_method(error):
    return jsonify({
                    "success": False,
                    "error": 405,
                    "message": "Method not allowed"
                    }), 405
