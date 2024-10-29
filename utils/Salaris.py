from utils.Belasting import Belasting


class Salaris:
    def __init__(
        self,
        bruto_per_maand: float,
        percentage_vakantiegeld: float = 8.0,
        percentage_eindejaars: float = 0,
        percentage_bonus: float = 0,
        bonus: float = 0,
    ):
        self.bruto_per_maand = bruto_per_maand
        self.percentage_vakantiegeld = percentage_vakantiegeld
        self.percentage_eindejaars = percentage_eindejaars
        self.percentage_bonus = percentage_bonus
        self.bonus = bonus

    def bereken_bruto_jaarlijks(self) -> float:
        som_percentages = (
            self.percentage_vakantiegeld
            + self.percentage_eindejaars
            + self.percentage_bonus
        )
        percentage = (100 + som_percentages) / 100
        return (12 * self.bruto_per_maand * percentage) + self.bonus

    def bereken_netto_jaarlijks(self, belasting: "Belasting") -> float:
        bruto_jaarlijks = self.bereken_bruto_jaarlijks()
        return belasting.bereken_netto_salaris(bruto_jaarlijks)
