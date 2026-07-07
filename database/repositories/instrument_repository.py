from database.database import Database


class InstrumentRepository:

    def __init__(self):

        self.db = Database()

    def save_all(
        self,
        instruments,
    ):

        self.db.execute(
            "DELETE FROM instruments"
        )

        rows = []

        for i in instruments:

            rows.append(

                (

                    i["instrument_token"],

                    i["exchange_token"],

                    i["tradingsymbol"],

                    i["name"],

                    i["last_price"],

                    i["expiry"],

                    i["strike"],

                    i["tick_size"],

                    i["lot_size"],

                    i["instrument_type"],

                    i["segment"],

                    i["exchange"],

                )

            )

        self.db.executemany(

            """

            INSERT INTO instruments

            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)

            """,

            rows,

        )

    def by_symbol(
        self,
        symbol,
    ):

        return self.db.fetchone(

            """

            SELECT *

            FROM instruments

            WHERE tradingsymbol=?

            """,

            (symbol,),

        )

    def token(
        self,
        symbol,
    ):

        row = self.by_symbol(
            symbol
        )

        if row:

            return row["instrument_token"]

        return None

    def symbols(
        self,
        exchange="NSE",
    ):

        rows = self.db.fetchall(

            """

            SELECT tradingsymbol

            FROM instruments

            WHERE exchange=?

            """,

            (exchange,),

        )

        return [

            r["tradingsymbol"]

            for r in rows

        ]