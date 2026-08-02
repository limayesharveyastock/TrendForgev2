class TargetManager:

    def next_target(

        self,

        position

    ):

        if position.ltp >= position.target1:

            return position.target2

        if position.ltp >= position.target2:

            return position.target3

        return position.target1