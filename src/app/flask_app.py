import logging

from flask import Flask, request
from flask_cors import CORS

from convert_link import get_init_item, convert_item
from helper import extract_web_info

app = Flask(__name__)
CORS(app)
logging.basicConfig(filename='logs.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')


@app.route('/convert', methods=['POST'])
def convert():
    # Get the init link from the request body
    init_link = request.get_json()['initLink']

    try:
        init_item, _ = get_init_item(init_link, logger=app.logger)
        result_item, _ = convert_item(init_item, logger=app.logger)

        # Return the result dictionary and a success message
        response = {'result': result_item.web_info,
                    'log': 'Conversion successful!'}

    except FileNotFoundError:
        response = {'result': extract_web_info(),
                    'log': 'Could not find track in Spotify...'}

    except Exception as e:
        app.logger.error(e)
        response = {'result': extract_web_info(),
                    'log': f'Something went wrong. ({e}) Please try again!'}

    return response


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
