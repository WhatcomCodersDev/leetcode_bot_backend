from flask import Flask, request
from app.routes import problem_routes, leaderboard_routes, challenges_routes, space_repetition_routes
from app.services import (redis_client, 
                          problem_manager, 
                          leaderboard_manager, 
                          leaderboard_collection_manager)

app = Flask(__name__)
app.register_blueprint(problem_routes.bp)
app.register_blueprint(leaderboard_routes.bp)
app.register_blueprint(challenges_routes.bp)
app.register_blueprint(space_repetition_routes.bp)

app.run(debug=True, port=8080, host="0.0.0.0")
