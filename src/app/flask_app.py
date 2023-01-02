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
    # Initialize the result dictionary
    init_result_dict = {'spotifyLink': '',
                   'img_src': '',
                   'info': {}}

    # Get the Deezer link from the request body
    deezer_link = request.get_json()['deezerLink']

    # Check if the Deezer link is valid
    deezer_link = check_deezer_link(deezer_link, logger=app.logger)
    if deezer_link is None:
        msg = 'Invalid Deezer link. Please try again!'
        app.logger.error(msg)
        return {'result': init_result_dict,
                'log': msg}

    try:
        # Convert using our script
        result_dict = convert_deezer_to_spotify(
            deezer_link, logger=app.logger)

        # Return the result dictionary and a success message
        response = {'result': result_dict,
                    'log': 'Conversion successful!'}

    except FileNotFoundError:
        response = {'result': init_result_dict,
                    'log': 'Could not find track in Spotify...'}

    except Exception as e:
        app.logger.error(e)
        response = {'result': init_result_dict,
                    'log': f'Something went wrong. ({e}) Please try again!'}

    return response


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
