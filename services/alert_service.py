from services.config_service import ConfigService


class AlertService:

    def __init__(self):

        self.config = ConfigService.load(
            "alerts.json"
        )

    def enabled(self):

        return self.config["enabled"]

    def minimum_score(self):

        return self.config["filters"]["minimum_score"]

    def allow_signal(
        self,
        signal,
    ):

        return signal in self.config["filters"]["signals"]

    def discord_enabled(self):

        return self.config["discord"]["enabled"]

    def webhook(self):

        return self.config["discord"]["webhook_url"]