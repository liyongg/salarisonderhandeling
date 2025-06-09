import math

import streamlit as st
from scipy.optimize import bisect

from utils.Belasting import Belasting
from utils.belastingstelsel import belastingstelsels
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
            max_value=1_000_000.0,
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
            value=f"€{salaris_netto_maand:,.2f}".translate(
                str.maketrans({",": ".", ".": ","})
            ),
            help="Indien *alle* bonussen maandelijks uitbetaald worden.",
        )
        with st.expander("Details"):
            st.write(
                f"Bruto belastingschijvern: €{belasting.bereken_bruto_belasting(salaris_bruto_jaar):.2f}"
            )
            st.write(
                f"Arbeidskorting = €{belasting.bereken_korting(salaris_bruto_jaar, 'arbeid'):.2f}"
            )
            st.write(
                f"Heffingskorting = €{belasting.bereken_korting(salaris_bruto_jaar, 'heffing'):.2f}"
            )


def bruto_for_netto(netto_target, belasting, bruto_min=1, bruto_max=1_000_000):
    def func(bruto):
        return belasting.bereken_netto_salaris(bruto) - netto_target

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
    wens_netto_maand_slider = (
        math.ceil((salaris_netto_maand + slider_value) / 50) * 50
    )
    wens_netto_maand_slider_bruto_jaar = bruto_for_netto(
        math.ceil((salaris_netto_maand + slider_value) / 50) * 50 * 12,
        belasting,
    )
    st.metric(
        label="Doel Netto (Maand)",
        value=f"€{wens_netto_maand_slider:,.0f}".replace(",", "."),
        help="Je gewenste netto salaris indien *alle* bonussen maandelijks uitbetaald worden.",
    )
    st.write(
        f"Bij salarisonderhandelingen moet je _€{wens_netto_maand_slider_bruto_jaar:,.2f}_ bruto per jaar vragen,".translate(
            str.maketrans({",": ".", ".": ","})
        ),
        f"Dat is _€{wens_netto_maand_slider_bruto_jaar - salaris_bruto_jaar:,.2f}_ meer dan nu,".translate(
            str.maketrans({",": ".", ".": ","})
        ),
    )
