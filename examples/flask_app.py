from flask import Flask, request, jsonify
from lynx_logger import LynxLogger, Level, Format
from lynx_logger.config import LogConfig, FileConfig
from lynx_logger.middleware import FlaskLoggingMiddleware


logger = LynxLogger(
    LogConfig(
        name="flask_app",
        level=Level.INFO,
        format=Format.JSON,
        log_to_console=True,
        file=FileConfig(
            enabled=True,
            filename="flask_app.log",
            max_size="10MB",
            backup_count=5,
            delay=True
        )
    )
)

app = Flask(__name__)
flask_logger = logger.get_logger()

FlaskLoggingMiddleware(app, flask_logger)

@app.route("/", methods=["GET"])
def read_root():
    logger.info("Hello, World!")
    return jsonify({"Hello": "World"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
