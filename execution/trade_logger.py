import csv
from pathlib import Path


class TradeLogger:

    FILE = Path("data/trades.csv")

    def log(self, trade):

        self.FILE.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        exists = self.FILE.exists()

        with open(

            self.FILE,

            "a",

            newline=""

        ) as f:

            writer = csv.writer(f)

            if not exists:

                writer.writerow([

                    "Date",

                    "Symbol",

                    "Side",

                    "Qty",

                    "Entry",

                    "Exit",

                    "PnL"

                ])

            writer.writerow([

                trade.entry_date,

                trade.symbol,

                trade.side,

                trade.quantity,

                trade.entry_price,

                trade.exit_price,

                trade.pnl

            ])