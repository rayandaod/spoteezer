import logging
import structlog

from flask import Flask, request
from flask_cors import CORS

from spoteezer.convert_link import get_item, convert_item

# Configure standard library logging
file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter("%(message)s"))

root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
root_logger.setLevel(logging.ERROR)

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

app = Flask(__name__)
CORS(app)

# Get a logger for the Flask app
LOGGER: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)
app.logger = LOGGER


@app.route("/convert", methods=["POST"])
def convert():
    """Creates an Item from the given URL, converts it
    into another item (Spotify or Deezer), and extract useful
    information for web display.

    Returns:
        dict: The response to the initial POST request.
    """

    LOGGER.info("conversion_started")

    # Get the init URL from the request body
    init_url = request.get_json().get("initURL", None)

    try:
        init_item = get_item(init_url)
        result_item = convert_item(init_item)

        # Return the result dictionary and a success message
        response = {
            "result": {"init": init_item.web_info, "result": result_item.web_info},
            "log": "Conversion successful!",
        }

    except FileNotFoundError:
        response = {"result": {}, "log": "Could not find track..."}

    except Exception as e:
        app.logger.error("conversion_error", exc_info=e, error=str(e))
        response = {
            "result": {},
            "log": f"Something went wrong.\n{e}\nPlease try again!",
        }

    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
