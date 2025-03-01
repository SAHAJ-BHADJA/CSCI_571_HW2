from flask import Flask, render_template, request, jsonify
import requests
import time
from config import ARTSY_CLIENT_ID, ARTSY_CLIENT_SECRET

app = Flask(__name__)

# Store token globally
ARTSY_TOKEN = None
ARTSY_TOKEN_EXPIRATION = 0

def get_artsy_token():

    global ARTSY_TOKEN, ARTSY_TOKEN_EXPIRATION
    if ARTSY_TOKEN and time.time() < ARTSY_TOKEN_EXPIRATION:
        return ARTSY_TOKEN

    url = "https://api.artsy.net/api/tokens/xapp_token"
    data = {"client_id": ARTSY_CLIENT_ID, "client_secret": ARTSY_CLIENT_SECRET}
    response = requests.post(url, data=data)

    if response.status_code == 201:
        token_data = response.json()
        ARTSY_TOKEN = token_data["token"]
        expiration_time = token_data["expires_at"]
        ARTSY_TOKEN_EXPIRATION = time.mktime(time.strptime(expiration_time, "%Y-%m-%dT%H:%M:%S+00:00"))
        return ARTSY_TOKEN
    else:
        raise Exception("Failed to obtain Artsy token")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search_artists():
    query = request.args.get('query', '')

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        headers = {"X-Xapp-Token": get_artsy_token()}
        url = f"https://api.artsy.net/api/search?q={query}&size=10&type=artist"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            search_results = response.json()
            artists = []
            
            for result in search_results["_embedded"]["results"]:
                if result["og_type"] == "artist":
                    artist_id = result["_links"]["self"]["href"].split("/")[-1]
                    artist_name = result["title"]
                    thumbnail_url = result["_links"]["thumbnail"]["href"]
                    if "missing_image.png" in thumbnail_url:
                        thumbnail_url = "https://via.placeholder.com/150"

                    artists.append({
                        "id": artist_id,
                        "name": artist_name,
                        "thumbnail": thumbnail_url
                    })

            return jsonify(artists)
        else:
            return jsonify({"error": "Failed to fetch search results"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/artist/<artist_id>', methods=['GET'])
def get_artist_details(artist_id):
    try:
        headers = {"X-Xapp-Token": get_artsy_token()}
        url = f"https://api.artsy.net/api/artists/{artist_id}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            artist_data = response.json()
            artist_details = {
                "id": artist_data.get("id", "Unknown"),
                "name": artist_data.get("name", "Unknown"),
                "birthday": artist_data.get("birthday", "N/A"),
                "deathday": artist_data.get("deathday", "N/A"),
                "nationality": artist_data.get("nationality", "Unknown"),
                "biography": artist_data.get("biography", "Biography not available"),
                "image": artist_data.get("_links", {}).get("thumbnail", {}).get("href", "https://via.placeholder.com/150")
            }
            return jsonify(artist_details)
        else:
            return jsonify({"error": "Failed to fetch artist details"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
