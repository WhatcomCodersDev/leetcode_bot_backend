from flask import Flask, request
from app.routes import problem_routes, leaderboard_routes, challenges_routes
from app.services import firestore_wrapper, redis_client, problem_manager, leaderboard_manager


app = Flask(__name__)

app.register_blueprint(problem_routes.bp)
app.register_blueprint(leaderboard_routes.bp)
app.register_blueprint(challenges_routes.bp)

app.run(debug=True)
