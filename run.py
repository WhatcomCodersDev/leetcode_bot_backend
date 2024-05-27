from flask import Flask, request
from app.routes import problem_routes, leaderboard_routes, challenges_routes, space_repetition_routes, users_routes
from app.services import (redis_client, 
                          problem_manager, 
                          leaderboard_manager, 
                          leaderboard_collection_manager)
from flask_cors import CORS


allowed_origins = [
    "http://localhost:3000",
    "https://www.whatcomcoders.com",
    "https://whatcomcoders.com",
]

app = Flask(__name__)
app.register_blueprint(problem_routes.bp)
app.register_blueprint(leaderboard_routes.bp)
app.register_blueprint(challenges_routes.bp)
app.register_blueprint(space_repetition_routes.bp)
app.register_blueprint(users_routes.bp)

CORS(app, resources={r"/*": {
        "origins": allowed_origins,
        "supports_credentials": True}}, supports_credentials=True)

app.run(debug=True, port=8080, host="0.0.0.0")
