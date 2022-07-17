class EloRateCalculator:
    k = 16

    @staticmethod
    def calculate(
            player_1_rate: int,
            player_2_rate: int,
            player_1_score: int,
            player_2_score: int) -> tuple[int, int]:
        e_1 = 1 / (1 + 10 ** ((player_2_rate - player_1_rate) / 400)) * (player_1_score + player_2_score)
        delta_1 = round(EloRateCalculator.k * (player_1_score - e_1))
        return player_1_rate + delta_1, player_2_rate - delta_1
