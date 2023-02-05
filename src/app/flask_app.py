import logging

from flask import Flask, request
from flask_cors import CORS

from convert_link import get_item, convert_item

app = Flask(__name__)
CORS(app)
logging.basicConfig(filename='logs.log',
                    level=logging.ERROR,
                    format='%(asctime)s %(levelname)s: %(message)s')


@app.route('/convert', methods=['POST'])
def convert():
    """Creates an Item from the given URL, converts it
    into another item (Spotify or Deezer), and extract useful
    information for web display.

    Returns:
        dict: The response to the initial POST request.
    """
    # Get the init URL from the request body
    init_url = request.get_json().get('initURL', None)

    try:
        init_item = get_item(init_url, logger=app.logger)
        result_item = convert_item(init_item, logger=app.logger)

        # Return the result dictionary and a success message
        response = {'result': {
            'init': init_item.web_info,
            'result': result_item.web_info},
                    'log': 'Conversion successful!'}

    except FileNotFoundError:
        response = {'result': {},
                    'log': 'Could not find track in Spotify...'}

    except Exception as e:
        app.logger.error(e)
        response = {'result': {},
                    'log': f'Something went wrong: {e} Please try again!'}

    return response


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
