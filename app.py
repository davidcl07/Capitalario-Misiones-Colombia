import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import json

# ---------- Configuración ----------
st.set_page_config(page_title="Capitalario Misiones Colombia", layout="centered")

# Constantes
GOOGLE_SHEET_NAME = "capitalario_misiones_colombia"
TIPOS_APORTE = ["Confío", "Rosario", "Eucaristía", "Visita al Santuario", "Otros"]
MIEMBROS = ["Padre Juan", "Padre Pablo", "David", "Teodoro"]
META = 50

# ---------- Autenticación con Google desde secrets ----------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
google_credentials = st.secrets["google"]

# Convertir secrets en dict para usar como credenciales
creds_dict = {
    "type": google_credentials["type"],
    "project_id": google_credentials["project_id"],
    "private_key_id": google_credentials["private_key_id"],
    "private_key": google_credentials["private_key"].replace("\\n", "\n"),
    "client_email": google_credentials["client_email"],
    "client_id": google_credentials["client_id"],
    "auth_uri": google_credentials["auth_uri"],
    "token_uri": google_credentials["token_uri"],
    "auth_provider_x509_cert_url": google_credentials["auth_provider_x509_cert_url"],
    "client_x509_cert_url": google_credentials["client_x509_cert_url"]
}

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1

# Leer datos
df = get_as_dataframe(sheet).dropna(how="all")
if df.empty:
    df = pd.DataFrame(columns=["Nombre", "Tipo", "FechaHora"])

total_general = len(df)

# ---------- UI PRINCIPAL ----------
st.title("Capitalario Misiones Colombia")
st.write("Capitalario de Gracias para seguir anhelando y conquistando este proyecto de fundar la juventud de Schoenstatt Colombia junto a la Mater")
st.subheader("Meta: 2000 contribuciones")

# ---------- Formulario ----------
st.subheader("➕ Agregar nueva contribución")
with st.form("form_ofrecimiento"):
    nombre = st.selectbox("Persona", MIEMBROS)
    tipo = st.selectbox("Contribución", TIPOS_APORTE)
    submit = st.form_submit_button("Agregar contribución")

    if submit:
        nueva_fila = pd.DataFrame({
            "Nombre": [nombre],
            "Tipo": [tipo],
            "FechaHora": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        df = pd.concat([df, nueva_fila], ignore_index=True)
        set_with_dataframe(sheet, df)
        st.success(f"¡Gracias {nombre} por ofrecer un(a) {tipo}!")
        st.rerun()

# ---------- Progreso general ----------
st.metric(label="Total acumulado", value=total_general)
progreso = min(total_general / META, 1.0) * 100

st.markdown(f"""
<div style="position: relative; height: 30px; background-color: #e0e0e0; border-radius: 10px;">
  <div style="
    background-color: #fb8500;
    width: {progreso}% ;
    height: 100%;
    border-radius: 10px;
    text-align: center;
    color: white;
    font-weight: bold;
    line-height: 30px;">
    {int(progreso)}%
  </div>
</div>
""", unsafe_allow_html=True)

# ---------- Gráficos ----------
conteo_tipos = df["Tipo"].value_counts().reindex(TIPOS_APORTE, fill_value=0)
faltantes = max(META - conteo_tipos.sum(), 0)
conteo_completo = conteo_tipos.copy()
conteo_completo["Faltantes"] = faltantes

col1, col2 = st.columns(2)

# Dona
with col1:
    st.markdown("<h2 style='font-size:25px; color:#333;'>Progreso por contribución</h2>", unsafe_allow_html=True)
    fig_dona = px.pie(
        names=conteo_completo.index,
        values=conteo_completo.values,
        hole=0.55,
        color=conteo_completo.index,
        color_discrete_map={
            "Confío": "#219ebc",
            "Rosario": "#023047",
            "Eucaristía": "#ffb703",
            "Visita al Santuario": "#fb8500",
            "Otros": "#8ecae6",
            "Faltantes": "#E0E0E0"
        }
    )
    fig_dona.update_traces(textinfo="percent", pull=[0.01]*len(conteo_completo))
    fig_dona.update_layout(showlegend=True, title=f"{conteo_tipos.sum()} de {META} contribuciones")
    st.plotly_chart(fig_dona, use_container_width=True)

# Barras por persona
with col2:
    st.markdown("<h2 style='font-size:25px; color:#333;'>Contribuciones por persona</h2>", unsafe_allow_html=True)
    df_conteo = df.groupby(["Nombre", "Tipo"]).size().reset_index(name="Cantidad")
    fig_bar = px.bar(
        df_conteo,
        x="Nombre",
        y="Cantidad",
        color="Tipo",
        title="Total por persona y tipo de oración",
        text="Cantidad",
        color_discrete_map={
            "Confío": "#219ebc",
            "Rosario": "#023047",
            "Eucaristía": "#ffb703",
            "Visita al Santuario": "#fb8500",
            "Otros": "#8ecae6"
        }
    )
    fig_bar.update_layout(
        barmode="stack",
        xaxis_title="Persona",
        yaxis_title="Contribuciones",
        legend_title="Tipo de oración"
    )
    st.plotly_chart(fig_bar, use_container_width=True)