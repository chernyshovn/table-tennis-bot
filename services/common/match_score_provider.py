from app import app
from database.models import Match
from models.match_score import MatchScore


class MatchScoreProvider:
    def get(self, match_id: int) -> MatchScore:
        with app.app_context():
            match = Match.query.filter_by(id=match_id).first()

            first_team_score = 0
            second_team_score = 0

            for game in match.games:
                if game.team_1_score > game.team_2_score:
                    first_team_score += 1
                elif game.team_1_score < game.team_2_score:
                    second_team_score += 1

            return MatchScore(
                first_team_score=first_team_score,
                second_team_score=second_team_score
            )
