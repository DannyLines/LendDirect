import re
import json
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g


app = Flask(__name__)

def calculateRange(user_input):
    new_string = user_input
    new_string = re.sub("[^0-9,-]", "", new_string).split(",")

    values = [int(x) for x in new_string]
    # Remove duplicates
    values = list(set(values))

    # Sort list
    values.sort()

    # Initialise variables
    max_ptr, cur_ptr, max_length, cur_length = 0, 0, 0, 0
    is_new_sequence = True

    # If the input has no or 1 input, can return the length of the input as answer to how wide the range is
    values_length = len(values)
    if values_length == 1:
        return [values[0], values[0]]

    # work through the list, using cur_ptr to point to the start index
    # of the sequence currently being counted, if the current value is equal to the previous value
    # plus one, then we want to increment the length of the current sequence range

    for i in range(1, values_length):
        if values[i] == (values[i - 1] + 1):
            cur_length += 1

            # If this range is greater than the current max_length, we have a new widest range
            if cur_length > max_length:
                max_length += 1

                # Update the max_ptr to be the ptr to the start of the current sequence
                # But only if this is a new sequence, prevents running this code multiple times
                # upon finding a new max sequence, i.e. max_length starts at 0, so if it finds
                # a run of 4 straight away, it would update max_ptr 4 times if we didnt check if it's a new sequence,
                # just to optimise the code a bit
                if is_new_sequence:
                    max_ptr = cur_ptr

                    # If we updated the max_ptr, must have been a new sequence so any subsequent checks will show its
                    # the same sequence
                    is_new_sequence = False
        else:
            # If not greater than max length, reset the current length and set is_new_sequence to true, as
            # we'll no be considering a new possible range.
            cur_length = 0
            is_new_sequence = True
            # handles edge case where max range starts on a value at index 0, without this will be a small bug
            # and omit the first value due to the loop starting at index 1
            if i == 1:
                cur_ptr = i
            else:
                # Incrememnt cur_ptr to point to ptr for possibel sequence
                cur_ptr = i + 1
    # After running, the start value for the max range will be at max_ptr
    # and the end value for this range will be our max_ptr + max_length
    max_range_start_val = values[max_ptr]
    max_range_end_val = values[max_ptr + max_length]
    return [max_range_start_val, max_range_end_val]


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Check if the request is for user input, handle and add to database
        if "user_input" in request.form:
            user_input = request.form["user_input"]
            max_range_start_val, max_range_end_val = calculateRange(user_input)

            user_input_json = json.dumps(user_input)
            conn = sqlite3.connect(DATABASE_NAME)
            cur = conn.cursor()

            cur.execute("INSERT INTO History (input, range_start, range_end) VALUES (?,?,?)",
                        (user_input_json, max_range_start_val, max_range_end_val))
            conn.commit()
            return render_template("index.html")
        # Check if request for navigation, then redirect
        elif "button_name" in request.form:
            nav_to = request.form['button_name']
            if nav_to == 'output':
                return redirect(url_for("output_page"))
            elif nav_to == 'history':
                return redirect(url_for("history_page"))
    else:
        return render_template("index.html")

@app.route("/output", methods=["GET", "POST"])
def output_page():
    if request.method == "POST":
        # Redirect if needed
        nav_to = request.form['button_name']
        if nav_to == 'home':
            return redirect(url_for("home"))
        elif nav_to == 'history':
            return redirect(url_for("history_page"))

    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()

    # Selects most recent entry from database
    get_all_query = "SELECT * FROM History ORDER BY id DESC LIMIT 1"
    cur.execute(get_all_query)
    # Get the valeus of most recent record in DB
    id, user_input, max_range_start_val, max_range_end_val = cur.fetchone()
    row =  cur.fetchone()
    conn.close()

    # Pass these values to the html file to be displayed
    return render_template(
        "output.html", user_input=user_input, output_val=[max_range_start_val, max_range_end_val]
        )

@app.route("/history", methods=["GET", "POST"])
def history_page():
    if request.method == "POST":
        # Handle navigation
        nav_to = request.form['button_name']
        if nav_to == 'home':
            return redirect(url_for("home"))
        elif nav_to == 'output':
            return redirect(url_for("output_page"))

    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()

    get_all_query = "SELECT * FROM History"
    cur.execute(get_all_query)

    # Take all results from database and load them into dictionary object history_results
    history_results = [dict(ID=row[0], Input=row[1], Start=row[2], End=row[3]) for row in cur.fetchall()]

    conn.close()
    # Pass this dictionary object to history.html to be rendered
    return render_template("history.html", rows=history_results)

if __name__ == "__main__":
    DATABASE_NAME = "database.db"
    conn = sqlite3.connect(DATABASE_NAME)
    setup_table = "CREATE TABLE IF NOT EXISTS History (id INTEGER PRIMARY KEY, input TEXT NOT NULL, range_start INTEGER NOT NULL, range_end INTEGER NOT NULL)"

    conn.cursor().execute(setup_table)
    app.run()