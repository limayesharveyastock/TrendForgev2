"""
report_generator.py
----------------------------------------------------------
TrendForge Report Generator

Features
--------
- Performance Report
- Portfolio Report
- Trade History Report
- CSV Export
- Excel Export
- JSON Export
"""

import json
import csv
from datetime import datetime
from pathlib import Path

try:
    from openpyxl import Workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class ReportGenerator:

    def __init__(self, output_directory="reports"):

        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------

    def _timestamp(self):

        return datetime.now().strftime("%Y%m%d_%H%M%S")

    # --------------------------------------------------

    def export_json(self, data, filename):

        filepath = self.output_directory / filename

        with open(filepath, "w", encoding="utf-8") as file:

            json.dump(
                data,
                file,
                indent=4,
                default=str
            )

        return str(filepath)

    # --------------------------------------------------

    def export_csv(self, records, filename):

        filepath = self.output_directory / filename

        if not records:
            return str(filepath)

        with open(
            filepath,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=records[0].keys()
            )

            writer.writeheader()

            writer.writerows(records)

        return str(filepath)

    # --------------------------------------------------

    def export_excel(self, records, filename):

        if not OPENPYXL_AVAILABLE:

            raise ImportError(
                "openpyxl is not installed."
            )

        workbook = Workbook()

        sheet = workbook.active

        if records:

            headers = list(records[0].keys())

            sheet.append(headers)

            for row in records:

                sheet.append(list(row.values()))

        filepath = self.output_directory / filename

        workbook.save(filepath)

        return str(filepath)

    # --------------------------------------------------

    def performance_report(self, analytics):

        report = analytics.report()

        filename = (
            f"performance_{self._timestamp()}.json"
        )

        return self.export_json(
            report,
            filename
        )

    # --------------------------------------------------

    def portfolio_report(self, portfolio):

        report = portfolio.portfolio_summary()

        filename = (
            f"portfolio_{self._timestamp()}.json"
        )

        return self.export_json(
            report,
            filename
        )

    # --------------------------------------------------

    def trade_history_report(self, analytics):

        trades = []

        for trade in analytics.trades:

            trades.append({

                "Symbol": trade.symbol,

                "Side": trade.side,

                "Quantity": trade.quantity,

                "Entry": trade.entry,

                "Exit": trade.exit,

                "PnL": trade.pnl,

                "Open Time": trade.open_time,

                "Close Time": trade.close_time

            })

        timestamp = self._timestamp()

        csv_file = self.export_csv(
            trades,
            f"trades_{timestamp}.csv"
        )

        excel_file = None

        if OPENPYXL_AVAILABLE:

            excel_file = self.export_excel(
                trades,
                f"trades_{timestamp}.xlsx"
            )

        json_file = self.export_json(
            trades,
            f"trades_{timestamp}.json"
        )

        return {

            "csv": csv_file,

            "excel": excel_file,

            "json": json_file

        }

    # --------------------------------------------------

    def full_report(
        self,
        analytics,
        portfolio
    ):

        return {

            "performance": self.performance_report(
                analytics
            ),

            "portfolio": self.portfolio_report(
                portfolio
            ),

            "trades": self.trade_history_report(
                analytics
            )

        }