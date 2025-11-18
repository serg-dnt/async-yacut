from http import HTTPStatus
from flask import jsonify, render_template, request
from . import app


class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return dict(message=self.message)

@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Page not found'}), HTTPStatus.NOT_FOUND
    return render_template('404.html'), HTTPStatus.NOT_FOUND

@app.errorhandler(500)
def internal_server_error(e):
    if request.path.startswith('/api/'):
        return (
            jsonify({'error': 'Internal server error'}),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR