import json

from flask import Flask, request, Response
from flask_cors import CORS

from convert_link import convert_deezer_to_spotify

app = Flask(__name__)
CORS(app)

@app.route('/convert', methods=['GET'])
def get_link():
    # Get the Deezer link from the request body
    deezer_link = request.get_json()['deezerLink']

    # Convert the Deezer link to a Spotify link using your Python script
    spotify_link = convert_deezer_to_spotify(deezer_link)

    # Return a JSON response with the Spotify link and any relevant log messages
    response = { 'spotifyLink': spotify_link, 'log': 'Conversion successful!' }

    response = Response(json.dumps(response), status=200, mimetype='application/json')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content-Type'] = 'application/json'
    
    return response

if __name__ == '__main__':
  app.run(host= '127.0.0.1:5000', debug=True)
