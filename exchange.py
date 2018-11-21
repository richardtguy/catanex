#!venv/bin/python
from app import app
if __name__ == '__main__':
    print("Starting development server...")
    app.run(
        host=app.config.get("HOST", "0.0.0.0"),
        port=app.config.get("PORT", 5000)
    )