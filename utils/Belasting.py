from typing import Literal

import numpy as np
from scipy.optimize import bisect

from utils.belastingstelsel import belastingstelsels
from utils.helpers import map_formatter


class Belasting:
    def __init__(self, jaar: int) -> None:
        if jaar not in belastingstelsels:
            raise NotImplementedError(f"Geen belastingstelsel voor {jaar}.")

        belastingjaar_stelsel = belastingstelsels[jaar]

        self.schijven = belastingjaar_stelsel["schijven"]
        self.arbeidskorting = belastingjaar_stelsel["arbeidskorting"]
        self.heffingskorting = belastingjaar_stelsel["heffingskorting"]

    def _bereken_bruto_belasting(self, bruto_jaarlijks: float) -> list:
        """
        Bereken de bruto belasting per schijf voor het gegeven bruto jaarlijks inkomen.
        Returnt een lijst met de belasting per schijf.
        """
        belasting_per_schijf: list[float] = []
        for (lower, upper), belasting_formule in self.schijven.items():
            belastbaar_inkomen = np.minimum(bruto_jaarlijks, upper) - lower
            belastbaar_inkomen = np.maximum(belastbaar_inkomen, 0)
            belasting_per_schijf.append(belasting_formule(belastbaar_inkomen))
        return belasting_per_schijf

    def bereken_bruto_belasting(
        self, bruto_jaarlijks: float, output: Literal["bedrag", "tekst"] = "bedrag"
    ) -> float | str:
        belasting_per_schijf = self._bereken_bruto_belasting(bruto_jaarlijks)
        if output == "tekst":
            tekst = ""
            for schijf in range(len(belasting_per_schijf)):
                if belasting_per_schijf[schijf] > 0:
                    tekst += f"- Schijf {schijf + 1}: €{belasting_per_schijf[schijf]:,.2f}".translate(
                        map_formatter
                    )
                    tekst += "\n\n"
            tekst += (
                f"Je totale belasting is €{sum(belasting_per_schijf):,.2f}".translate(
                    map_formatter
                )
            )
            return tekst
        elif output == "bedrag":
            return sum(belasting_per_schijf)
        else:
            raise ValueError("Output moet 'bedrag' of 'tekst' zijn.")

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


def bruto_for_netto(
    netto_target, belasting: Belasting, bruto_min=1, bruto_max=1_000_000_000
):
    def func(bruto):
        return belasting.bereken_netto_salaris(bruto) - netto_target

    return bisect(func, bruto_min, bruto_max)
