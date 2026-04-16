from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

def create_app(config_class=Config):
    """Factory function to create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for frontend integration
    CORS(app, resources={r"/api/*": {"origins": ["https://ai-learning-systems.vercel.app", "http://localhost:5000", "http://127.0.0.1:5000"]}})
    
    # Future Blueprint registrations
    from routes.auth_routes import auth_bp
    from routes.task_routes import task_bp
    from routes.planner_routes import planner_bp
    from routes.insights_routes import insights_bp
    from routes.recommendation_routes import recommendation_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(task_bp, url_prefix='/api/tasks')
    app.register_blueprint(planner_bp, url_prefix='/api/planner')
    app.register_blueprint(insights_bp, url_prefix='/api/insights')
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommendations')
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Simple health check endpoint."""
        return jsonify({
            "status": "healthy", 
            "service": "AI Productivity OS Backend",
            "version": "1.0.0"
        }), 200

    @app.route('/', methods=['GET'])
    def home():
        """Root endpoint for deployment verification."""
        return "AI Productivity OS API is running!", 200
        
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
