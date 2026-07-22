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