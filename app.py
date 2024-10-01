from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

app = Flask(__name__)

app.debug = True
app.config['SECRET_KEY'] = 'secretkey'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False  

toolbar = DebugToolbarExtension(app)

responses = []

@app.route("/")
def show_survey_start():
    """Show the start page for the survey."""
    return render_template("start.html", survey=survey)


@app.route("/begin", methods=["POST"])
def start_survey():
    """Clear the session of responses."""
    session["responses"] = []
    return redirect("/questions/0")


@app.route("/answer", methods=["POST"])
def handle_question():
    """Save response and redirect to next question."""

    # get user's answer from the form submission
    choice = request.form.get('answer')

    if not choice:
        flash("You must select an answer.")
        return redirect(f"/questions/{len(session['responses'])}")

    # add this response to the session
    responses = session.get("responses", [])
    responses.append(choice)
    session["responses"] = responses  # Store the updated responses back in session

    if len(responses) == len(survey.questions):
        return redirect("/complete")
    else:
        return redirect(f"/questions/{len(responses)}")


@app.route("/questions/<int:qid>")
def show_question(qid):
    """Display current question."""
    responses = session.get("responses", [])

    if responses is None:
        return redirect("/")

    if len(responses) == len(survey.questions):
        return redirect("/complete")

    # preventing skipping questions.
    if len(responses) != qid:
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]
    return render_template("question.html", question_num=qid, question=question)


@app.route("/complete")
def complete():
    """Survey complete. Show completion page."""
    return render_template("thank_you.html")

# to check for responses in session storage
@app.route("/view-session")
def view_session():
    """View session data in the browser."""
    responses = session.get("responses", [])
    return f"Session data: {responses}"