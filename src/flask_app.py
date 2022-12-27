import json

from flask import Flask, request, Response
from flask_cors import CORS

from convert_link import convert_deezer_to_spotify

app = Flask(__name__)
CORS(app)

@app.route('/convert', methods=['POST'])
def convert():
    # Get the Deezer link from the request body
    deezer_link = request.data.decode('utf-8')

    # Convert the Deezer link to a Spotify link using your Python script
    spotify_link = convert_deezer_to_spotify(deezer_link)

    # Return a JSON response with the Spotify link and any relevant log messages
    response = { 'spotifyLink': spotify_link, 'log': 'Conversion successful!' }

    response = Response(json.dumps(response), status=200, mimetype='application/json')
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    return response

if __name__ == '__main__':
  app.run()
