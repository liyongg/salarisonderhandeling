import math

import streamlit as st
from scipy.optimize import bisect

from utils.Belasting import Belasting, bruto_for_netto
from utils.belastingstelsel import belastingstelsels
from utils.helpers import map_formatter
from utils.Salaris import Salaris

# Global predefined settings
input_belastingjaar = max(belastingstelsels.keys())
input_maand_of_jaar = "Maandelijks"

st.set_page_config(page_title="Salarisonderhandeling", page_icon="💸", layout="wide")

with st.sidebar:
    with st.popover("Opties"):
        input_belastingjaar: int = st.selectbox(
            label="Belastingjaar",
            options=sorted(belastingstelsels.keys(), reverse=True),
        )
        input_maand_of_jaar: str = st.selectbox(
            label="Salarisbasis", options=["Maandelijks", "Jaarlijks"]
        )

        belasting = Belasting(jaar=input_belastingjaar)

    if input_maand_of_jaar == "Maandelijks":
        st.write(f"*Belastingjaar **{input_belastingjaar}***")

        input_salaris: float = st.number_input(
            label="Bruto Salaris (€/maand)",
            value=3500.00,
            min_value=0.00,
            max_value=1_000_000.0,
            step=100.00,
        )

        col1, col2 = st.columns(2)

        with col1:
            input_vakantiegeld: float = st.number_input(
                label="Vakantiegeld (%)", value=8.00, min_value=8.00, max_value=100.0
            )
            input_bonus_perc: float = st.number_input(
                label="Bonus (%)", value=0.00, min_value=0.00, max_value=100.0
            )
            input_bonus_abs: float = st.number_input(
                label="Bonus (€)",
                value=0.00,
                min_value=0.00,
                max_value=1_000_000.0,
                help="Bruto bonus per jaar",
            )

        with col2:
            input_eindejaars: float = st.number_input(
                label="Eindejaars (%)",
                value=100 / 12,
                min_value=0.0,
                max_value=100.0,
                help="Ook bekend als persoonlijk keuzebudget",
            )
            input_pensioen_perc: float = st.number_input(
                label="Pensioen (%)",
                value=0.00,
                min_value=0.00,
                max_value=100.0,
                help="Procent bruto maandelijks salaris naar pensioen.",
            )
            input_vergoeding: float = st.number_input(
                label="Vergoeding (Netto)",
                value=0.00,
                min_value=0.00,
                max_value=1_000_000.0,
                help="Zoals thuiswerk- of internetvergoeding per maand.",
            )

        input_bruto_netto_ruil: float = st.number_input(
            label="Bruto-Netto Ruil (€/Maand)",
            value=0.00,
            min_value=0.00,
            max_value=input_salaris,
            help="Zoals een vitaliteitsverlof",
        )
    elif input_maand_of_jaar == "Jaarlijks":
        input_salaris_jaar = st.number_input(
            label="Bruto Salaris (€/jaar)",
            value=45000.00,
            min_value=0.00,
            max_value=100_000_000.0,
            step=100.00,
        )

if input_maand_of_jaar == "Maandelijks":
    salaris = Salaris(
        bruto_per_maand=input_salaris,
        percentage_vakantiegeld=input_vakantiegeld,
        percentage_eindejaars=input_eindejaars,
        percentage_bonus=input_bonus_perc,
        percentage_pensioen=input_pensioen_perc,
        bonus=input_bonus_abs,
        bruto_netto_ruil=input_bruto_netto_ruil,
        vergoeding=input_vergoeding,
    )

    salaris_bruto_jaar = salaris.bereken_bruto_jaarlijks()
    salaris_netto_jaar = salaris.bereken_netto_jaarlijks(belasting=belasting)
elif input_maand_of_jaar == "Jaarlijks":
    salaris_bruto_jaar = input_salaris_jaar
    salaris_netto_jaar = belasting.bereken_netto_salaris(salaris_bruto_jaar)

salaris_netto_maand = salaris_netto_jaar / 12

metric_col1, metric_col2 = st.columns(2)

with metric_col1:
    st.metric(
        label="Bruto (Jaar)",
        value=f"€{salaris_bruto_jaar:,.0f}".replace(",", "."),
    )
    st.metric(
        label="Netto (Jaar)",
        value=f"€{salaris_netto_jaar:,.0f}".replace(",", "."),
    )
    with st.container():
        st.metric(
            label="Netto (Maand)",
            value=f"€{salaris_netto_maand:,.2f}".translate(map_formatter),
            help="Indien *alle* bonussen maandelijks uitbetaald worden.",
        )
        with st.expander("Details"):
            st.write("### Belasting")
            belasting_belastbaar_inkomen = belasting.bereken_bruto_belasting(
                salaris_bruto_jaar
            )
            st.write(
                belasting.bereken_bruto_belasting(salaris_bruto_jaar, output="tekst")
            )
            st.write("### Kortingen")
            arbeidskorting = belasting.bereken_korting(salaris_bruto_jaar, "arbeid")
            heffingskorting = belasting.bereken_korting(salaris_bruto_jaar, "heffing")
            kortingen = arbeidskorting + heffingskorting
            st.write(
                f"- Arbeidskorting: €{arbeidskorting:,.2f}\n"
                f"- Heffingskorting: €{heffingskorting:,.2f}\n\n"
                f"Je hebt in totaal €{kortingen:,.2f} aan kortingen".translate(
                    map_formatter
                )
            )
            st.write("## Berekening")
            st.write(
                f"- Bruto Salaris: €{salaris_bruto_jaar:,.2f}\n"
                f"- Belasting: €{belasting_belastbaar_inkomen:,.2f}\n"
                f"- Kortingen: €{arbeidskorting + heffingskorting:,.2f}\n\n"
                f"Netto salaris = Bruto Salaris - (Belasting - Kortingen)\n\n"
                f"Netto salaris = €{salaris_bruto_jaar:,.2f} - (€{belasting_belastbaar_inkomen:,.2f} - €{kortingen:,.2f})\n\n"
                f"Netto salaris = €{salaris_netto_jaar:,.2f}\n\n"
                f"Je netto salaris is dus €{salaris_netto_jaar:,.2f} per jaar ofwel €{salaris_netto_maand:,.2f} per maand".translate(
                    map_formatter
                )
            )
            st.write("### Uitleg")
            st.write(
                """
                Om je netto salaris te berekenen, moet eerst het belastbaar inkomen 
                worden berekend. Dit is inclusief vakantiegeld, eindejaarsuitkering, en 
                eventuele bonussen. Gezamenlijk vormt dit het belastbaar inkomen.
                
                Het belastbaar inkomen wordt gebruikt om te bepalen hoeveel belasting je
                moet betalen per schijf. Ook wordt het belastbaar inkomen gebruikt om
                de arbeidskorting en heffingskorting te berekenen, die beide van invloed
                zijn op je uiteindelijke netto salaris. Er geldt: hoe hoger je 
                belastbaar inkomen, hoe minder korting je krijgt.
                """
            )


def bruto_for_netto_maandelijks(
    netto_target,
    bruto_min=1,
    bruto_max=1_000_000_000,
):
    def func(bruto):
        salaris_instance = Salaris(
            bruto_per_maand=bruto,
            percentage_vakantiegeld=input_vakantiegeld,
            percentage_eindejaars=input_eindejaars,
            percentage_bonus=input_bonus_perc,
            percentage_pensioen=input_pensioen_perc,
            bonus=input_bonus_abs,
            bruto_netto_ruil=input_bruto_netto_ruil,
            vergoeding=input_vergoeding,
        )
        return (
            salaris_instance.bereken_netto_jaarlijks(belasting=belasting) - netto_target
        )

    return bisect(func, bruto_min, bruto_max)


with metric_col2:
    slider_value = st.slider(
        label="Hoeveel €50en netto meer per maand is je doel?",
        min_value=0,
        max_value=2000,
        value=0,
        step=50,
        help="Afgerond naar boven per €50.",
        format="€%d",
    )
    wens_netto_maand_slider = math.ceil((salaris_netto_maand + slider_value) / 50) * 50
    wens_netto_maand_slider_bruto_jaar = bruto_for_netto(
        wens_netto_maand_slider * 12,
        belasting,
    )
    st.metric(
        label="Doel Netto (Maand)",
        value=f"€{wens_netto_maand_slider:,.0f}".replace(",", "."),
        help="Je gewenste netto salaris indien *alle* bonussen maandelijks uitbetaald worden.",
    )
    st.write(
        f"Om _€{wens_netto_maand_slider - salaris_netto_maand:,.2f}_ meer te verdienen moet je bij salarisonderhandelingen _€{wens_netto_maand_slider_bruto_jaar:,.2f}_ bruto per jaar vragen,".translate(
            map_formatter
        ),
        f"Dat is _€{wens_netto_maand_slider_bruto_jaar - salaris_bruto_jaar:,.2f}_ meer dan nu,".translate(
            map_formatter
        ),
    )
    if input_maand_of_jaar == "Maandelijks":
        wens_netto_maand_bruto_maand = bruto_for_netto_maandelijks(
            wens_netto_maand_slider * 12
        )
        st.write(
            f"Met dezelfde percentages en bonussen is dat _€{wens_netto_maand_bruto_maand:,.2f}_ bruto per maand dat je moet vragen,".translate(
                map_formatter
            ),
            f"Dat is _€{wens_netto_maand_bruto_maand - input_salaris:,.2f}_ meer dan nu,".translate(
                map_formatter
            ),
        )
