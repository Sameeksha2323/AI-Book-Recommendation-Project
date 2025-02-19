import pickle
import numpy as np

# Load model files inside Cerebrium
books = pickle.load(open('books.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))
popular_df = pickle.load(open('popular.pkl', 'rb'))

PLACEHOLDER_IMAGE_URL = "https://placehold.co/150x150/png"
books = books.fillna('') # Fill other string columns with empty strings as before

# Specifically fill NaN in 'Image-URL-M' column with the placeholder image URL
books['Image-URL-M'] = books['Image-URL-M'].fillna(PLACEHOLDER_IMAGE_URL)

similarity_scores = np.nan_to_num(similarity_scores, nan=0.0, posinf=0.0, neginf=0.0) # For numpy arrays
pt = pt.fillna(0) # For pandas DataFrames/Series

popular_df = popular_df.fillna(0)

def run(type="recommendation", book_name=""): # Use named parameters with defaults
    """Handles incoming requests and returns book recommendations OR popular books."""
    request_type = type # Use the 'type' named parameter directly
    if request_type == "popular_books":
        # Return popular books data
        popular_books_data = []
        top_20_popular_df = popular_df.head(20)
        for index, row in top_20_popular_df.iterrows():
            popular_books_data.append({
                "title": row['Book-Title'],
                "author": row['Book-Author'],
                "image": row['Image-URL-M']
            })
        return {"popular_books": popular_books_data}

    elif request_type == "recommendation":
        # Existing book recommendation logic
        # book_name = request.get("book_name", "") # No longer using request.get()
        # book_name is now directly from the named parameter
        try:
            index_pos = np.where(pt.index == book_name)[0][0]
            similar_items = sorted(list(enumerate(similarity_scores[index_pos])), key=lambda x: x[1], reverse=True)[1:5]

            recommendations = []
            for i in similar_items:
                temp_df = books[books['Book-Title'] == pt.index[i[0]]]
                recommendations.append({
                    "title": temp_df.drop_duplicates('Book-Title')['Book-Title'].values[0],
                    "author": temp_df.drop_duplicates('Book-Title')['Book-Author'].values[0],
                    "image": temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values[0]
                })

            return {"recommendations": recommendations}

        except IndexError:
            return {"error": "Book not available in the database."}
    else:
        return {"error": "Invalid request type. Use 'recommendation' or 'popular_books'."}