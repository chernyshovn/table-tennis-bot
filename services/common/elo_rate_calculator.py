from enums.match_result import MatchResult


class EloRateCalculator:
    k = 16

    @staticmethod
    def calculate(
            player_1_rate: int,
            player_2_rate: int,
            match_result: MatchResult) -> tuple[int, int]:
        e_1 = 1 / (1 + 10 ** ((player_2_rate - player_1_rate) / 400))

        if match_result == MatchResult.FIRST_PLAYER_WON:
            s_1 = 1
        elif match_result == MatchResult.SECOND_PLAYER_WON:
            s_1 = 0
        elif match_result == MatchResult.DRAW:
            s_1 = 0.5
        else:
            s_1 = 0.5

        delta_a = round(EloRateCalculator.k * (s_1 - e_1))
        return player_1_rate + delta_a, player_2_rate - delta_a
