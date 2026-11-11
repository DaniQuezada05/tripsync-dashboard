import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config (page_title="TripSync · Big Data", page_icon="✈️", layout="wide")

AZUL = "#2a78d6"
GRIS = "#c9c8c2"
TINTA = "#52514e"
SECUENCIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
RANGOS = ["0-2 km", "2-5 km", "5-10 km", "10-20 km", "20-40 km"]


@st.cache_data
def cargar (nombre):
    return pd.read_csv (f"data/{nombre}.csv")


resumen = cargar ("kpi_resumen_zonas")
cat = cargar ("kpi1_por_categoria")
dist = cargar ("kpi2_por_distancia")
mensual = cargar ("kpi3_mensual")
causas = cargar ("kpi3_causas_retraso")
estado = cargar ("estado_vuelos")
rutas = cargar ("co2_rutas_principales")
top = cargar ("top_lugares")
mapa = cargar ("mapa_lugares_buenos")
anual = cargar ("resenas_por_anio")
volumen = cargar ("volumen_datos")

ZONAS = resumen.sort_values ("zona")["zona"].tolist ()


def estilo (fig, alto=380):
    fig.update_layout (height=alto, margin=dict (l=10, r=10, t=40, b=10),
                       plot_bgcolor="white", paper_bgcolor="white",
                       font=dict (color=TINTA, size=13), hoverlabel=dict (bgcolor="white"),
                       showlegend=False)
    fig.update_xaxes (showgrid=False, linecolor="#e4e3df")
    fig.update_yaxes (gridcolor="#efeeea", zeroline=False)
    return fig


def barras_ranking (df, col, titulo, sufijo="", decimales=1, ascendente=False):
    d = df.sort_values (col, ascending=not ascendente)
    colores = [AZUL if z == ciudad else GRIS for z in d["zona"]]
    fig = go.Figure (go.Bar (
        x=d[col], y=d["zona"], orientation="h", marker_color=colores,
        marker_line_width=0, text=[f"{v:,.{decimales}f}{sufijo}" for v in d[col]],
        textposition="outside", textfont=dict (color=TINTA),
        hovertemplate="%{y}: %{x:,." + str (decimales) + "f}" + sufijo + "<extra></extra>"))
    fig.update_layout (title=titulo, bargap=0.35)
    fig.update_xaxes (showticklabels=False, range=[0, d[col].max () * 1.18])
    return estilo (fig, 40 * len (d) + 60)


with st.sidebar:
    st.title ("✈️ TripSync")
    st.caption ("Planificador de viajes en grupo · Big Data · UABC Grupo 361")
    ciudad = st.selectbox ("Ciudad a analizar", ZONAS, index=ZONAS.index ("Santa Barbara") if "Santa Barbara" in ZONAS else 0)
    st.divider ()
    st.markdown ("**KPIs**")
    st.markdown ("1. Calificación ponderada → **¿a dónde ir?**\n2. Caminabilidad → **¿cómo moverse?**\n3. Puntualidad → **¿cuándo ir?**")
    st.divider ()
    st.caption ("Fuentes: Yelp Open Dataset · U.S. DOT Bureau of Transportation Statistics (2025) · factores de emisión EPA")

fila = resumen.set_index ("zona").loc[ciudad]
n = len (resumen)

t0, t1, t2, t3, t4, t5 = st.tabs (["Resumen", "KPI 1 · ¿A dónde?", "KPI 2 · ¿Cómo moverse?",
                                    "KPI 3 · ¿Cuándo?", "Impacto ambiental", "Datos"])

with t0:
    st.header (f"{ciudad}")
    c1, c2, c3, c4 = st.columns (4)
    c1.metric ("KPI 1 · Calificación ponderada", f"{fila['kpi1_calificacion_ponderada']:.2f} ★",
               f"#{int (fila['rank_kpi1'])} de {n}", delta_color="off")
    c2.metric ("KPI 2 · Lugares buenos a ≤ 2 km", f"{fila['kpi2_pct_caminable']:.1f} %",
               f"#{int (fila['rank_kpi2'])} de {n}", delta_color="off")
    c3.metric ("KPI 3 · Vuelos puntuales", f"{fila['kpi3_pct_puntual']:.1f} %",
               f"#{int (fila['rank_kpi3'])} de {n}", delta_color="off")
    c4.metric ("CO₂ promedio para llegar", f"{fila['co2_prom_kg_pasajero']:.0f} kg",
               "por pasajero", delta_color="off")

    st.markdown (
        f"Mejor mes para volar: **{MESES[int (fila['mejor_mes']) - 1]}** · "
        f"Peor mes: **{MESES[int (fila['peor_mes']) - 1]}** · "
        f"{int (fila['lugares']):,} lugares turísticos abiertos con {int (fila['resenas']):,} reseñas")

    st.subheader ("Comparativo de las 10 ciudades")
    tabla = resumen[["zona", "kpi1_calificacion_ponderada", "kpi2_pct_caminable", "kpi3_pct_puntual",
                     "co2_prom_kg_pasajero", "rank_kpi1", "rank_kpi2", "rank_kpi3"]].copy ()
    tabla["rank_promedio"] = tabla[["rank_kpi1", "rank_kpi2", "rank_kpi3"]].mean (axis=1).round (1)
    tabla = tabla.sort_values ("rank_promedio")
    st.dataframe (
        tabla, hide_index=True, width="stretch",
        column_config={
            "zona": "Ciudad",
            "kpi1_calificacion_ponderada": st.column_config.NumberColumn ("KPI 1 ★", format="%.2f"),
            "kpi2_pct_caminable": st.column_config.ProgressColumn ("KPI 2 % caminable", format="%.1f%%", min_value=0, max_value=100),
            "kpi3_pct_puntual": st.column_config.ProgressColumn ("KPI 3 % puntual", format="%.1f%%", min_value=0, max_value=100),
            "co2_prom_kg_pasajero": st.column_config.NumberColumn ("CO₂ kg/pasajero", format="%.0f"),
            "rank_kpi1": "Lugar KPI 1", "rank_kpi2": "Lugar KPI 2", "rank_kpi3": "Lugar KPI 3",
            "rank_promedio": st.column_config.NumberColumn ("Lugar promedio", format="%.1f"),
        })
    st.caption ("Lugar promedio = promedio de las posiciones en los 3 KPIs (1 = mejor). Ordena la tabla dando clic en una columna.")

with t1:
    st.header ("KPI 1 · Calificación ponderada por destino")
    st.markdown ("Promedio de la **calificación bayesiana** de los lugares turísticos abiertos. "
                 "Un lugar con pocas reseñas se acerca al promedio general; uno con muchas conserva su calificación. "
                 "Le da al grupo un criterio objetivo para **votar el destino**.")
    a, b = st.columns ([1, 1.3])
    with a:
        st.plotly_chart (barras_ranking (resumen, "kpi1_calificacion_ponderada", "Calificación ponderada (★)", " ★", 2), width="stretch")
    with b:
        piv = cat[cat["categoria_principal"] != "Sin categoría"].pivot (index="categoria_principal", columns="zona", values="calificacion_ponderada")
        fig = px.imshow (piv, text_auto=".2f", aspect="auto", color_continuous_scale=SECUENCIAL,
                         labels=dict (color="★", x="", y=""))
        fig.update_layout (title="Calificación por categoría y ciudad")
        fig.update_traces (hovertemplate="%{x} · %{y}: %{z:.2f} ★<extra></extra>")
        st.plotly_chart (estilo (fig, 460), width="stretch")

    st.subheader (f"Top 20 lugares en {ciudad}")
    st.dataframe (top[top["zona"] == ciudad].drop (columns=["zona"]), hide_index=True, width="stretch",
                  column_config={"posicion": "#", "nombre": "Lugar", "categoria_principal": "Categoría",
                                 "calificacion_ponderada": st.column_config.NumberColumn ("Calificación ponderada", format="%.2f ★"),
                                 "num_resenas": "Reseñas", "dist_centro_km": st.column_config.NumberColumn ("Km al centro", format="%.1f")},
                  column_order=["posicion", "nombre", "categoria_principal", "calificacion_ponderada", "num_resenas", "dist_centro_km"])

with t2:
    st.header ("KPI 2 · Índice de caminabilidad")
    st.markdown ("De los lugares turísticos abiertos con **4★ o más**, qué porcentaje está a **2 km o menos del centro** (≈ 25 min a pie). "
                 "Entre más alto, más del itinerario se recorre caminando o en transporte público → **menos CO₂ durante el viaje**.")
    a, b = st.columns ([1, 1.3])
    with a:
        st.plotly_chart (barras_ranking (resumen, "kpi2_pct_caminable", "% de lugares buenos a ≤ 2 km", " %"), width="stretch")
        d = dist[dist["zona"] == ciudad].set_index ("rango_distancia").reindex (RANGOS).fillna (0).reset_index ()
        fig = go.Figure (go.Bar (x=d["rango_distancia"], y=d["lugares_buenos"],
                                 marker_color=[AZUL] + [GRIS] * 4, marker_line_width=0,
                                 hovertemplate="%{x}: %{y:,} lugares<extra></extra>"))
        fig.update_layout (title=f"Lugares buenos por distancia al centro · {ciudad}", bargap=0.35)
        st.plotly_chart (estilo (fig, 320), width="stretch")
    with b:
        m = mapa[mapa["zona"] == ciudad].copy ()
        m["ubicacion"] = m["dist_centro_km"].le (2).map ({True: "≤ 2 km del centro", False: "Más de 2 km"})
        fig = px.scatter_map (m, lat="latitud", lon="longitud", color="ubicacion",
                              color_discrete_map={"≤ 2 km del centro": AZUL, "Más de 2 km": "#9a9992"},
                              hover_name="nombre", hover_data={"categoria_principal": True, "estrellas_yelp": True,
                                                                "dist_centro_km": ":.1f", "latitud": False, "longitud": False, "ubicacion": False},
                              zoom=9.5, map_style="carto-positron", opacity=0.75)
        fig.update_traces (marker=dict (size=8))
        fig.update_layout (title=f"Lugares con 4★ o más · {ciudad}", height=620, margin=dict (l=0, r=0, t=40, b=0),
                           legend=dict (orientation="h", y=1.02, x=0, title=None), showlegend=True)
        st.plotly_chart (fig, width="stretch")

with t3:
    st.header ("KPI 3 · Puntualidad de vuelos por destino y mes")
    st.markdown ("% de vuelos que **llegaron a tiempo** (menos de 15 min de retraso, sin cancelarse ni desviarse) al aeropuerto de cada ciudad en 2025. "
                 "Ayuda a **votar las fechas** con menos riesgo de retrasos, cancelaciones y gastos imprevistos.")
    fig = go.Figure ()
    for z in ZONAS:
        d = mensual[mensual["zona"] == z].sort_values ("mes")
        es = z == ciudad
        fig.add_trace (go.Scatter (x=[MESES[i - 1] for i in d["mes"]], y=d["pct_puntual"], name=z, mode="lines+markers" if es else "lines",
                                   line=dict (color=AZUL if es else GRIS, width=3 if es else 1.5),
                                   marker=dict (size=8), hovertemplate=z + " · %{x}: %{y:.1f}%<extra></extra>"))
    fig.data = tuple (sorted (fig.data, key=lambda t: t.name == ciudad))
    fig.update_layout (title=f"% de vuelos puntuales por mes · {ciudad} (azul) vs. otras ciudades (gris)")
    fig.update_yaxes (ticksuffix=" %")
    st.plotly_chart (estilo (fig, 400), width="stretch")

    a, b = st.columns (2)
    with a:
        st.plotly_chart (barras_ranking (resumen, "kpi3_pct_puntual", "% puntual anual", " %"), width="stretch")
    with b:
        c = causas[causas["zona"] == ciudad].melt (id_vars="zona", var_name="causa", value_name="pct")
        c["causa"] = c["causa"].map ({"pct_aerolinea": "Aerolínea", "pct_clima": "Clima", "pct_sistema_aereo": "Sistema aéreo",
                                      "pct_seguridad": "Seguridad", "pct_avion_tarde": "Avión llegó tarde"})
        c = c.sort_values ("pct")
        fig = go.Figure (go.Bar (x=c["pct"], y=c["causa"], orientation="h", marker_color=AZUL, marker_line_width=0,
                                 text=[f"{v:.1f} %" for v in c["pct"]], textposition="outside", textfont=dict (color=TINTA),
                                 hovertemplate="%{y}: %{x:.1f}% de los minutos de retraso<extra></extra>"))
        fig.update_layout (title=f"¿Por qué se retrasan los vuelos? · {ciudad}", bargap=0.35)
        fig.update_xaxes (showticklabels=False, range=[0, c["pct"].max () * 1.25])
        st.plotly_chart (estilo (fig, 300), width="stretch")
        e = estado[estado["zona"] == ciudad].set_index ("estado_vuelo").reindex (["A tiempo", "Retrasado", "Cancelado", "Desviado"]).fillna (0)
        tot = e["vuelos"].sum ()
        st.caption (" · ".join (f"**{k}:** {v / tot * 100:.1f} %" for k, v in e["vuelos"].items ()) + f" · de {int (tot):,} vuelos")

with t4:
    st.header ("Impacto ambiental")
    st.markdown ("TripSync puede recomendar destinos con **menos emisiones**: llegar con un vuelo más corto y moverse a pie en el destino. "
                 "CO₂ estimado con factores del EPA por pasajero-milla según la distancia del vuelo (corto < 300 mi: 0.207 · medio: 0.130 · largo ≥ 2,300 mi: 0.162 kg).")
    a, b = st.columns (2)
    with a:
        st.plotly_chart (barras_ranking (resumen, "co2_prom_kg_pasajero", "CO₂ promedio por pasajero para llegar (kg) · menor es mejor", " kg", 0, ascendente=True), width="stretch")
    with b:
        fig = px.scatter (resumen, x="co2_prom_kg_pasajero", y="kpi2_pct_caminable", text="zona",
                          labels={"co2_prom_kg_pasajero": "CO₂ para llegar (kg por pasajero)", "kpi2_pct_caminable": "% caminable (KPI 2)"})
        fig.update_traces (marker=dict (size=12, color=[AZUL if z == ciudad else "#9a9992" for z in resumen["zona"]],
                                        line=dict (color="white", width=2)),
                           textposition="top center", textfont=dict (color=TINTA, size=11),
                           hovertemplate="%{text}<br>CO₂: %{x:.0f} kg<br>Caminable: %{y:.1f}%<extra></extra>")
        fig.update_layout (title="Destinos ideales: arriba a la izquierda (poco CO₂ y muy caminables)")
        st.plotly_chart (estilo (fig, 460), width="stretch")

    st.subheader (f"Rutas con más vuelos hacia {ciudad}")
    r = rutas[rutas["zona"] == ciudad].sort_values ("co2_kg_pasajero")
    fig = go.Figure (go.Bar (x=r["co2_kg_pasajero"], y=r["ciudad_origen"], orientation="h", marker_color=AZUL, marker_line_width=0,
                             customdata=r[["distancia_km", "vuelos"]],
                             text=[f"{v:.0f} kg" for v in r["co2_kg_pasajero"]], textposition="outside", textfont=dict (color=TINTA),
                             hovertemplate="%{y}<br>%{customdata[0]:,.0f} km · %{customdata[1]:,} vuelos al año<br>%{x:.0f} kg CO₂ por pasajero<extra></extra>"))
    fig.update_xaxes (showticklabels=False, range=[0, r["co2_kg_pasajero"].max () * 1.2])
    fig.update_layout (bargap=0.3)
    st.plotly_chart (estilo (fig, 32 * len (r) + 60), width="stretch")

with t5:
    st.header ("Volumen de datos")
    v = volumen.copy ()
    v["pasa_200k"] = v["pasa_200k"].map ({True: "✅ Sí", False: "— (tabla de apoyo)"})
    st.dataframe (v, hide_index=True, width="stretch",
                  column_config={"tabla": "Tabla", "registros_dataset_completo": st.column_config.NumberColumn ("Registros en el dataset completo", format="%,d"),
                                 "registros_que_usamos": st.column_config.NumberColumn ("Registros analizados", format="%,d"),
                                 "pasa_200k": "¿Más de 200 mil?"})
    s = anual.groupby ("anio", as_index=False)["resenas"].sum ()
    fig = go.Figure (go.Bar (x=s["anio"], y=s["resenas"], marker_color=AZUL, marker_line_width=0,
                             hovertemplate="%{x}: %{y:,} reseñas<extra></extra>"))
    fig.update_layout (title="Reseñas de Yelp por año (10 ciudades)", bargap=0.25)
    st.plotly_chart (estilo (fig, 320), width="stretch")
    st.markdown (
        "**Limitaciones**\n"
        "- BTS solo incluye vuelos dentro de EE. UU.: el KPI 3 mide la confiabilidad del aeropuerto de destino, no de un vuelo desde México.\n"
        "- La caminabilidad usa la distancia al centro; no considera banquetas ni rutas de transporte.\n"
        "- Las reseñas de Yelp llegan a enero de 2022 y los vuelos son de 2025; no se cruzan por fecha, se unen por ciudad y aeropuerto.")
