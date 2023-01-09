import logging

from flask import Flask, request
from flask_cors import CORS

from convert_link import get_spotify_item, get_init_item

app = Flask(__name__)
CORS(app)
logging.basicConfig(filename='logs.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')


@app.route('/convert', methods=['POST'])
def convert():
    # Initialize the result dictionary
    init_result_dict = {'initLink': '',
                        'resultLink': '',
                        'img_src': '',
                        'info': {}}

    # Get the Deezer link from the request body
    init_link = request.get_json()['initLink']
    
    try:
        # Get the item from the link
        item = get_init_item(init_link, logger=app.logger)

        # Convert using our script
        result_dict = get_spotify_item(
            init_link, logger=app.logger)

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
