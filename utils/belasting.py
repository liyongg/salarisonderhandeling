from typing import Literal

import numpy as np

from utils.belastingstelsel import belastingstelsels


class Belasting:
    def __init__(self, jaar: int) -> None:

        if jaar not in belastingstelsels:
            raise NotImplementedError(f"Geen belastingstelsel voor {jaar}.")

        belastingjaar_stelsel = belastingstelsels[jaar]

        self.schijven = belastingjaar_stelsel["schijven"]
        self.arbeidskorting = belastingjaar_stelsel["arbeidskorting"]
        self.heffingskorting = belastingjaar_stelsel["heffingskorting"]

    def bereken_bruto_belasting(self, bruto_jaarlijks: float) -> float:
        belasting_per_schijf: list[float] = []
        for (lower, upper), belasting_formule in self.schijven.items():
            belastbaar_inkomen = np.minimum(bruto_jaarlijks, upper) - lower
            belastbaar_inkomen = np.maximum(belastbaar_inkomen, 0)
            belasting_per_schijf.append(belasting_formule(belastbaar_inkomen))
        return sum(belasting_per_schijf)

    def bereken_korting(
        self, bruto_jaarlijks: float, type: Literal["arbeid", "heffing"]
    ) -> float:
        kortingen = {
            "arbeid": self.arbeidskorting,
            "heffing": self.heffingskorting,
        }
        tarieven = kortingen[type]

        for (lower, upper), formule in tarieven.items():
            if lower <= bruto_jaarlijks < upper:
                return formule(bruto_jaarlijks)
        raise ValueError("Salaris is niet gedefinieerd in de tarieven.")

    def bereken_netto_belasting(self, bruto_jaarlijks: float) -> float:
        bruto_belasting = self.bereken_bruto_belasting(bruto_jaarlijks)

        arbeidskorting = self.bereken_korting(bruto_jaarlijks, "arbeid")
        heffingskorting = self.bereken_korting(bruto_jaarlijks, "heffing")
        kortingen = arbeidskorting + heffingskorting

        return max(bruto_belasting - kortingen, 0)

    def bereken_netto_salaris(self, bruto_jaarlijks: float) -> float:
        inkomstenbelasting = self.bereken_netto_belasting(bruto_jaarlijks)
        return bruto_jaarlijks - inkomstenbelasting
