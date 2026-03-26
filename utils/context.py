from datetime import datetime

def register_context_processors(app):
    @app.context_processor
    def inject_globals():
        return dict(now=datetime.now())
