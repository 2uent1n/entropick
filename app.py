import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Load environment variables from .env file
load_dotenv()


def main() -> None:
    """Main entry point for the EntroPick application."""
    app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()


if __name__ == "__main__":
    main()
