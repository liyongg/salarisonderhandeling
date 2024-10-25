import streamlit as st

with st.sidebar:
    st.write("Vul hier je gegevens in")
    input_salaris = st.number_input(label="Bruto Salaris (€/maand)", value=3500.00, min_value=0.00)
    input_vakantiegeld = st.number_input(label="Vakantiegeld (%)", value=8.00, min_value=8.00)
    input_13e = st.number_input(label="13e maand (%)", value=100/12, min_value=0.0)
    input_bonus_abs = st.number_input(label="Bonus (€)", value=0.00, min_value=0.00)
    input_bonus_perc = st.number_input(label="Bonus (%)", value=0.00, min_value=0.00)
