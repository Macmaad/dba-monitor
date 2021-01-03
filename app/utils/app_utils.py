import logging
import json
from http import HTTPStatus
import atexit

import logmatic
import requests
from apscheduler.schedulers.background import BackgroundScheduler

GOOGLE_CHAT_WEBHOOK = "https://chat.googleapis.com/v1/spaces/AAAA9dMeL0g/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=03y0q7CqGrReKW2xSi9CDfnTCaBKscfhRjc9Eg2EP98%3D"


def get_logger():
    new_logger = logging.getLogger()
    flask_logger = logging.getLogger("werkzeug")
    scheduler = logging.getLogger("apscheduler.scheduler")
    scheduler_default = logging.getLogger("apscheduler.executors.default")
    flask_logger.setLevel(logging.ERROR)
    scheduler.setLevel(logging.ERROR)
    scheduler_default.setLevel(logging.ERROR)
    if new_logger.hasHandlers():
        for hdlr in new_logger.handlers:
            new_logger.removeHandler(hdlr)
    if logmatic:
        handler = logging.StreamHandler()
        log_format = logmatic.JsonFormatter(
            fmt="%(levelname) %(asctime) %(name) %(processName) %(filename) %(funcName) %(lineno) %(module) "
            "%(message)"
        )
        handler.setFormatter(log_format)
    else:
        handler = logging.StreamHandler()
    new_logger.addHandler(handler)
    new_logger.setLevel(logging.INFO)
    return new_logger


logger = get_logger()


def read_json_file(path):
    data = dict()
    with open(path) as json_file:
        data = json.load(json_file)

    return data


def send_google_chat_message(message):
    response = {"statusCode": HTTPStatus.BAD_REQUEST}

    res = requests.post(
        GOOGLE_CHAT_WEBHOOK,
        json={"text": message},
        headers={"Content-Type": "application/json; charset=UTF-8"},
    )

    if res.status_code == HTTPStatus.OK:
        logger.info("Message was sent successful", extra={"response": res.json()})
        response = {"statusCode": HTTPStatus.OK}

    else:
        logger.error(
            "Something went wrong sending the message",
            extra={"response": res.json()},
        )
        response = {"statusCode": HTTPStatus.INTERNAL_SERVER_ERROR}

    return response


def add_background_cron(function, trigger, seconds):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=function, trigger=trigger, seconds=seconds)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())