from flask import Flask


app = Flask(__name__)


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Study Tracker</title>
        </head>

        <body>
            <h1>Study Tracker</h1>

            <p>
                Track your study sessions, goals,
                progress, and consistency.
            </p>

            <h2>Web Version</h2>

            <p>
                My Study Tracker is now running in the browser!
            </p>
        </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)