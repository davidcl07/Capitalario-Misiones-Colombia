import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# ---------- Configuración ----------
st.set_page_config(page_title="Capitalario Misiones Colombia", layout="centered")

# Constantes
CSV_FILE = "capitalario_colombia.csv"
TIPOS_APORTE = ["Confío", "Rosario", "Eucaristía", "Visita al Santuario", "Otros"]
MIEMBROS = ["Padre Juan", "Padre Pablo", "David", "Teodoro"]
META = 50

# Crear archivo si no existe
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["Nombre", "Tipo", "FechaHora"])
    df_init.to_csv(CSV_FILE, index=False)

# Cargar datos
df = pd.read_csv(CSV_FILE)
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
        nueva_fila.to_csv(CSV_FILE, mode='a', header=False, index=False)
        st.success(f"¡Gracias {nombre} por ofrecer un(a) {tipo}!")
        st.rerun()

st.metric(label="Total acumulado", value=total_general)
progreso = min(total_general / META, 1.0) * 100

st.markdown(f"""
<div style="position: relative; height: 30px; background-color: #e0e0e0; border-radius: 10px;">
  <div style="
    background-color: #fb8500;
    width: {progreso}%;
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

# ---------- Agrupar datos por tipo ----------
conteo_tipos = df["Tipo"].value_counts().reindex(TIPOS_APORTE, fill_value=0)

# Añadir fila para "Faltantes"
faltantes = max(META - conteo_tipos.sum(), 0)
conteo_completo = conteo_tipos.copy()
conteo_completo["Faltantes"] = faltantes

# ---------- Visualización en 2 columnas ----------
col1, col2 = st.columns(2)

# ---------- Gráfico de dona (anillo) con cada tipo + faltantes en gris ----------
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

# ---------- Gráfico de barras apiladas por persona y tipo ----------
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