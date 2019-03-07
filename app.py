from flaskblog import create_app
import os

app = create_app()

# If you don't want to use environment variables you can do this:
if __name__ == "__main__":
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)

# Alternatively you can set environment variables as:
# set FLASK_APP = your_init_file.py
# set FLASK_DEBUG = 1
# flask run
# This allows us to use the flask shell for debugging puporposes
