"""
Risk Service
Finance Utility Suite

Responsible for calculating stock risk metrics.
"""


class RiskService:

    # ---------------------------------
    # Beta Risk
    # ---------------------------------

    def get_beta_risk(self, beta):

        if beta is None:
            return "Unknown"

        if beta < 0.80:
            return "Low"

        elif beta <= 1.20:
            return "Moderate"

        else:
            return "High"

    # ---------------------------------
    # Investment Score
    # ---------------------------------

    def investment_score(self, data):

        score = 100

        beta = data.get("Beta")

        pe = data.get("PE")

        dividend = data.get("Dividend Yield")

        if beta is not None:

            if beta > 1.5:
                score -= 25

            elif beta > 1.2:
                score -= 15

        if pe is not None:

            if pe > 50:
                score -= 20

            elif pe > 30:
                score -= 10

        if dividend is not None:

            if dividend > 0:
                score += 5

        score = max(0, min(score, 100))

        return score

    # ---------------------------------
    # Rating
    # ---------------------------------

    def star_rating(self, score):

        if score >= 90:
            return "⭐⭐⭐⭐⭐"

        elif score >= 75:
            return "⭐⭐⭐⭐"

        elif score >= 60:
            return "⭐⭐⭐"

        elif score >= 40:
            return "⭐⭐"

        return "⭐"
