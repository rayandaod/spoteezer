import logging

from flask import Flask, request
from flask_cors import CORS

from convert_link import convert_deezer_to_spotify, check_deezer_link

app = Flask(__name__)
CORS(app)
logging.basicConfig(filename='logs.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')


@app.route('/convert', methods=['POST'])
def get_link():
    # Get the Deezer link from the request body
    deezer_link = request.get_json()['deezerLink']

    # Check if the Deezer link is valid
    deezer_link = check_deezer_link(deezer_link, logger=app.logger)
    if deezer_link is None:
      msg = 'Invalid Deezer link. Please try again!'
      app.logger.error(msg)
      return {'spotifyLink': '',
              'img_src': '',
              'log': msg}

    try:
      # Convert the Deezer link to a Spotify link using your Python script
      spotify_link, img_link = convert_deezer_to_spotify(deezer_link, logger=app.logger)
      response = {'spotifyLink': spotify_link,
                  'img_src': img_link,
                  'log': 'Conversion successful! Click on the link above!'}

    except FileNotFoundError:
      response = {'spotifyLink': '',
                  'img_src': '',
                  'log': 'Could not find track in Spotify!'}

    except Exception as e:
      app.logger.error(e)
      response = {'spotifyLink': '',
                  'img_src': '',
                  'log': 'Something went wrong!'}

    return response


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
