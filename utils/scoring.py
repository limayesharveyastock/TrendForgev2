def band_score(value, bands):

    """
    bands

    [

      (30,8),

      (25,7),

      (20,6),

      (15,4),

      (10,2),

      (0,0)

    ]

    """

    for minimum, score in bands:

        if value >= minimum:

            return score

    return 0

    class ScoreNormalizer:

    @staticmethod
    def normalize(

        value,

        minimum,

        maximum,

    ):

        if maximum == minimum:

            return 0

        return (

            (

                value -

                minimum

            )

            /

            (

                maximum -

                minimum

            )

        ) * 100