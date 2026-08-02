class ReportGenerator:

    def generate(

        self,

        metrics

    ):

        return {

            "Trades": metrics.total_trades,

            "Wins": metrics.wins,

            "Losses": metrics.losses,

            "Win Rate": metrics.win_rate,

            "Net Profit": metrics.net_profit,

            "Average Profit": metrics.average_profit,

            "Average Loss": metrics.average_loss,

            "Expectancy": metrics.expectancy,

        }