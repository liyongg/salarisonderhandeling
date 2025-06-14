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
        Bereken de bruto belasting per schijf op basis van het bruto jaarlijkse
        inkomen. Niet bedoeld voor publieke gebruik, maar voor interne berekeningen.

        Args:
            bruto_jaarlijks (float): Het bruto jaarlijks inkomen dat gebruikt wordt voor
            de berekening van de belasting per schijf.

        Returns:
            list: Een lijst met de berekende belastingen voor elke schijf, waarbij elke
            index overeenkomt met een belasting schijf.
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
        """
        Bereken de bruto belasting op basis van het bruto jaarlijkse inkomen.
        Args:
            bruto_jaarlijks (float): Het bruto jaarinkomen waarop de belasting wordt berekend.
            output (Literal["bedrag", "tekst"], optional): Het gewenste outputformaat.
                - "bedrag": Geeft het totaalbedrag van de berekende belasting terug.
                - "tekst": Geeft een overzichtelijke tekstuele weergave van de belasting per schijf terug.
                Standaardwaarde is "bedrag".
        Returns:
            float | str:
                - Als output "bedrag" is, retourneert de functie het totale belastingbedrag (float).
                - Als output "tekst" is, retourneert de functie een tekstuele samenvatting (str)
                  van de belastingbedragen per schijf inclusief het totaal.
        Raises:
            ValueError: Als de parameter 'output' een waarde ontvangt die niet "bedrag" of "tekst" is.
        """

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
        """
        Bereken de korting op basis van het bruto jaarlijkse inkomen.

        Deze functie bepaalt, op basis van het opgegeven inkomen en kortingstype, de
        toepasbare korting volgens gedefinieerde tarieven. Het tarief wordt gezocht
        binnen de bijbehorende limieten en de bijbehorende formule wordt toegepast op
        het bruto inkomen.

        Args:
            bruto_jaarlijks (float): Het bruto jaarlijkse inkomen.
            type (Literal["arbeid", "heffing"]): Het type korting, waarbij 'arbeid' de
                arbeidskorting vertegenwoordigt en 'heffing' de heffingskorting.

        Returns:
            float: De berekende korting op het opgegeven bruto jaarlijkse inkomen.

        Raises:
            ValueError: Als er geen tarief wordt gevonden dat overeenkomt met het opgegeven
                bruto jaarlijkse inkomen.
        """
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
        """
        Bereken de netto belasting voor een jaarlijks bruto inkomen.

        Deze methode berekent eerst de bruto belasting op basis van het opgegeven jaarlijkse bruto inkomen.
        Vervolgens worden de arbeidskorting en heffingskorting berekend en hiervan afgetrokken van de bruto belasting.
        Indien de resulterende netto belasting negatief is, wordt 0 geretourneerd.

        Args:
            bruto_jaarlijks (float): Het jaarlijkse bruto inkomen.

        Returns:
            float: De berekende netto belasting, waarbij gegarandeerd is dat deze niet negatief is.
        """
        bruto_belasting = self.bereken_bruto_belasting(bruto_jaarlijks)

        arbeidskorting = self.bereken_korting(bruto_jaarlijks, "arbeid")
        heffingskorting = self.bereken_korting(bruto_jaarlijks, "heffing")
        kortingen = arbeidskorting + heffingskorting

        return max(bruto_belasting - kortingen, 0)

    def bereken_netto_salaris(self, bruto_jaarlijks: float) -> float:
        """
        Bereken het netto jaarlijkse salaris na aftrek van de inkomstenbelasting.

        Args:
            bruto_jaarlijks (float): Het bruto salaris op jaarbasis.

        Returns:
            float: Het netto salaris na aftrek van de berekende inkomstenbelasting.

        Notes:
            Deze methode gebruikt de functie 'bereken_netto_belasting' om de verschuldigde inkomstenbelasting te berekenen.
        """
        inkomstenbelasting = self.bereken_netto_belasting(bruto_jaarlijks)
        return bruto_jaarlijks - inkomstenbelasting


def bruto_for_netto(
    netto_target, belasting: Belasting, bruto_min=1, bruto_max=1_000_000_000
):
    """
    Bereken het bruto salaris dat overeenkomt met een gegeven netto doelwaarde.

    Args:
        netto_target (float): Het gewenste netto salaris.
        belasting (Belasting): Een instantie van de Belasting Class, welke de methode 'bereken_netto_salaris' bevat om het netto salaris te berekenen.
        bruto_min (float, optional): De minimale waarde voor het bruto salaris bij het zoeken. Default is 1.
        bruto_max (float, optional): De maximale waarde voor het bruto salaris bij het zoeken. Default is 1_000_000_000.

    Returns:
        float: Het berekende bruto salaris dat resulteert in het gewenste netto salaris.
    """

    def func(bruto):
        return belasting.bereken_netto_salaris(bruto) - netto_target

    return bisect(func, bruto_min, bruto_max)
