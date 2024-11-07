import streamlit as st

from utils.Belasting import Belasting
from utils.Salaris import Salaris

# Global predefined settings
input_belastingjaar = 2024
input_maand_of_jaar = "Maandelijks"

with st.sidebar:

    with st.popover("Opties"):
        input_belastingjaar: int = st.selectbox(
            label="Belastingjaar", options=[2024, 2025]
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
        )


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
salaris_netto_maand = salaris_netto_jaar / 12
st.metric(
    label="Bruto (Jaar)",
    value=f"€{salaris_bruto_jaar:,.2f}",
)
st.metric(
    label="Netto (Jaar)",
    value=f"€{salaris_netto_jaar:,.2f}",
)
st.metric(
    label="Netto (Maand)",
    value=f"€{salaris_netto_maand:,.2f}",
    help="Indien *alle* bonussen maandelijks uitbetaald worden.",
)
