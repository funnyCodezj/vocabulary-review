"""
SM-2 Algorithm implementation.
Based on SuperMemo SM-2 as used by Anki.

quality: 0-5 user rating
  0 - complete blackout
  1 - incorrect, but upon seeing answer, remembered
  2 - incorrect, but felt familiar
  3 - correct, with serious difficulty
  4 - correct, after hesitation
  5 - perfect, effortless recall
"""


def sm2_calculate(quality: int, repetition: int, ease_factor: float, interval: int):
    if quality < 3:
        # incorrect: reset
        repetition = 0
        interval = 1
    else:
        # correct
        if repetition == 0:
            interval = 1
        elif repetition == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)

        repetition += 1

    # update ease factor
    new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if new_ef < 1.3:
        new_ef = 1.3

    # stage mapping
    if repetition == 0:
        stage = 0
    elif interval <= 1:
        stage = 1
    elif interval <= 7:
        stage = 2
    elif interval <= 21:
        stage = 3
    elif interval <= 60:
        stage = 4
    else:
        stage = 5

    return stage, repetition, round(new_ef, 2), interval
