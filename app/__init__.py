from flask import Flask

def create_app():
    app = Flask(__name__)

    # Register blueprints for different parts of the app
    from .routes import ai_chatbot_bp
    app.register_blueprint(ai_chatbot_bp)

    return app
