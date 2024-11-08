from utils.Belasting import Belasting


class Salaris:
    def __init__(
        self,
        bruto_per_maand: float,
        percentage_vakantiegeld: float = 8.0,
        percentage_eindejaars: float = 0,
        percentage_bonus: float = 0,
        percentage_pensioen: float = 0,
        bonus: float = 0,
        bruto_netto_ruil: float = 0,
        vergoeding: float = 0,
    ):
        self.bruto_per_maand = bruto_per_maand
        self.percentage_vakantiegeld = percentage_vakantiegeld
        self.percentage_eindejaars = percentage_eindejaars
        self.percentage_bonus = percentage_bonus
        self.percentage_pensioen = percentage_pensioen
        self.bonus = bonus
        self.bruto_netto_ruil = bruto_netto_ruil
        self.vergoeding = vergoeding

    def bereken_bruto_jaarlijks(self) -> float:
        som_percentages = (
            self.percentage_vakantiegeld
            + self.percentage_eindejaars
            + self.percentage_bonus
            - self.percentage_pensioen
        )
        percentage = (100 + som_percentages) / 100

        maandelijks_salaris = self.bruto_per_maand - self.bruto_netto_ruil
        return (12 * maandelijks_salaris * percentage) + self.bonus

    def bereken_netto_jaarlijks(self, belasting: "Belasting") -> float:
        bruto_jaarlijks = self.bereken_bruto_jaarlijks()
        netto_jaarlijks = belasting.bereken_netto_salaris(bruto_jaarlijks)
        return netto_jaarlijks + 12 * (self.bruto_netto_ruil + self.vergoeding)
