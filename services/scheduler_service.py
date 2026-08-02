from apscheduler.schedulers.background import BackgroundScheduler


class SchedulerService:

    def __init__(self):

        self.scheduler = BackgroundScheduler()

    def add_scan_job(

        self,

        func,

        minutes=5

    ):

        self.scheduler.add_job(

            func,

            "interval",

            minutes=minutes

        )

    def start(self):

        self.scheduler.start()

    def shutdown(self):

        self.scheduler.shutdown()