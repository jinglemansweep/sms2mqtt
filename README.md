# SMS2MQTT

A simple SMS to MQTT gateway for polling TextLocal API and publishing any received SMS text messages to an MQTT broker.

## Requirements

* MQTT Server (e.g. Mosquitto)
* API Key, Inbox ID from TextLocal SMS service

You will need an account at TextLocal to use their excellent SMS services. A free account provides you with a fixed keyword (e.g. `ABCDE`) on one of their shared short numbers (e.g. `60777`). Messages can be sent to the short number but the message must contain the fixed keyword in order for it to be processed.

Once you have an account, [create an API Key](https://control.txtlocal.co.uk/settings/apikeys/) and then find the `Inbox ID` of the inbox you want to monitor. You can find thise by going to the [View Inboxes](https://control.txtlocal.co.uk/messages/), expanding the required inbox and clicking `View Inbox`. The URL of the resulting page should look like: `https://control.txtlocal.co.uk/messages/?id=10`. In this example, the ID of the inbox is `10`.

## Installation

Create a virtual environment, and install dependencies:

    python -m venv ./venv
    source ./venv/bin/activate
    poetry install # or 'pip install .'

Configure the project by either creating a `.env` file (see [`.env.example`](./.env.example) for details):

    cp ./.env.example ./.env
    ${EDITOR} ./.env

Start the project using Docker and Compose:

    docker compose up -d --build

Or within your local development environment:

    python3 ./sms2mqtt/__init__.py


