from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# --- Cerebrium API Configuration ---
CEREBRIUM_API_URL = "https://api.cortex.cerebrium.ai/v4/p-5d57b63b/book-recommender-project/run"
#https://api.cortex.cerebrium.ai/v4/p-5d57b63b/book-recommender-project/<your-function>
CEREBRIUM_API_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiJwLTVkNTdiNjNiIiwibmFtZSI6IiIsImRlc2NyaXB0aW9uIjoiIiwiZXhwIjoyMDU1NDcwNTQ0fQ.JGZxKx5vQZug4Y5tkEPvOB5qoEKkkVHfrZDw8-no1etYEYHHOqUVHD8r4n8xLu_g24oQA09v8Ab9aSUGjjUge8aFtW2bmq_tH0IOrrmvMrCN4Xz_jeExwbPES5m-mpv0LggGpxUoR9HczBYQ4XEVCKJMc5cs3GB-MVj184ChfOP3U3vN8YC70bUXUfEMJ9UDUrvzFQkSORUgzwUgQDNEQlGNshn804-Wt4_sq1E2bHYI8abJO7flw1UxJTBZJTo7FN6yLKl1jMYpack3Pl8d8K75jf5vFGpvHISVqsZKUx6HMaULrzxwyUkpPwtlMPqgWY25fWVuXg42VtYgehvV5w"

if not CEREBRIUM_API_URL or not CEREBRIUM_API_KEY:
    print("Warning: CEREBRIUM_API_URL or CEREBRIUM_API_KEY environment variables not set!")

HEADERS = { # Using HEADERS instead of headers for consistency in code style
  'Authorization': f'Bearer {CEREBRIUM_API_KEY}',
  'Content-Type': 'application/json'
}
# -----------------------------------


@app.route('/')
def index():
    try:
        response = requests.post(CEREBRIUM_API_URL, headers=HEADERS, json={"type": "popular_books"})
        response.raise_for_status()
        api_data = response.json()

        if "result" in api_data and "popular_books" in api_data["result"]: # <-- Check for "result" AND "popular_books" inside "result"
            popular_books = api_data["result"]["popular_books"] # <-- Access popular_books through "result"
            book_names = [book['title'] for book in popular_books]
            authors = [book['author'] for book in popular_books]
            images = [book['image'] for book in popular_books]

            return render_template('fun.html',
                                   book_name=book_names,
                                   author=authors,
                                   image=images
                                   )

        else:
            return render_template('index.html', error_message="Unexpected API response format") # More specific error message


    except requests.exceptions.RequestException as e:
        print(f"Error fetching popular books from API: {e}")
        return render_template('index.html', error_message="Error connecting to book data API")


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input_book = request.form.get('user_input')

    try:
        response = requests.post(CEREBRIUM_API_URL, json={"type": "recommendation", "book_name": user_input_book}, headers=HEADERS)
        response.raise_for_status()
        api_data = response.json()

        if "result" in api_data and "error" in api_data["result"]: # Check for "error" inside "result"
            return render_template('recommend.html', not_found_message=api_data["result"]["error"], book_name=user_input_book) # Access error through "result"
        elif "result" in api_data and "recommendations" in api_data["result"]: # Check for "result" and "recommendations" inside "result"
            recommendations = api_data["result"]["recommendations"] # Access recommendations through "result"
            return render_template('recommend.html', recommendations=recommendations, book_name=user_input_book, not_found_message="")
        else:
            return render_template('recommend.html', not_found_message="Unexpected API response format", book_name=user_input_book) # More specific error message

    except requests.exceptions.RequestException as e:
        print(f"Error fetching recommendations from API: {e}")
        return render_template('recommend.html', not_found_message="Error connecting to recommendation API", book_name=user_input_book) # Handle connection error, pass book_name

if __name__ == '__main__':
    app.run(debug=True)