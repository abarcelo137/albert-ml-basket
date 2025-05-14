import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import base64
import plotly.express as px
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="Dream Team NBA", layout="wide", page_icon="🏀")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color:#f5f6fa;
    }
    .card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        margin-bottom: 2.0rem;
    }
    .card h3 {
        margin: 0 0 0.8rem 0;
        font-weight:600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 1. Charger les fichiers
df_team = pd.read_csv("Data final/dream_teams_2000_2024.csv", sep=";")
df_infos = pd.read_csv("Data final/df_final_players_stats.csv")

tab1, tab2 = st.tabs(["🏀 Dream Team", "📊 Stats d'Équipe"])

# ✅ Debug : afficher les colonnes si besoin

with tab1:
    st.title("🏀 Dream Team de la saison")
    # 2. Sélection de la saison
    if "season" in df_team.columns:
        saisons = sorted(df_team["season"].dropna().unique())
        col_left, col_center, col_right = st.columns([1, 6, 1])
        with col_center:
            saison_choisie = st.select_slider(
                "", 
                options=saisons,
                value=saisons[0],
                help="Glisse ou clique sur une saison"
    )


        # 3. Filtrer les joueurs de cette saison
        dream_team = df_team[df_team["season"] == saison_choisie]

        # 4. Affichage horizontal des joueurs avec flèches
            # 4. Affichage avec flèches gauche/droite (avec boucle)
        st.subheader("Joueurs sélectionnés")

        # Liste des joueurs
        player_names = dream_team["player_name"].tolist()
        total_players = len(player_names)
        player_line = ", ".join([f"<strong>{name}</strong>" for name in player_names])
        st.markdown(
    f"<p style='font-size:18px; margin-bottom: 1rem;'>{player_line}</p>",
    unsafe_allow_html=True
)



        # Initialiser l'index du joueur dans session_state
        if 'player_index' not in st.session_state:
            st.session_state.player_index = 0

        # Affichage des boutons flèches
        col1, col2, col3 = st.columns([1, 5, 1])

        with col1:
            if st.button("⬅️", use_container_width=True):
                st.session_state.player_index = (st.session_state.player_index - 1) % total_players

        with col3:
            if st.button("➡️", use_container_width=True):
                st.session_state.player_index = (st.session_state.player_index + 1) % total_players

        # Récupération du joueur sélectionné
        selected_player = player_names[st.session_state.player_index]

        with col2:
            st.markdown(f"### **{selected_player}**", unsafe_allow_html=True)

        # Récupération de la ligne joueur
        row = dream_team[dream_team["player_name"] == selected_player].iloc[0]
        infos = df_infos[df_infos["player_name"] == selected_player]
        infos = infos.iloc[0] if not infos.empty else None

        # Affichage des infos joueur
        # Affichage des infos joueur AVEC PHOTO
        if infos is not None:
            col_center = st.columns([1, 5, 1])[1]  # pour centrer au milieu

            with col_center:
                col_photo, col_desc = st.columns([1, 2], gap="large")  # gauche = image, droite = texte

                with col_photo:
                    player_image_base = selected_player.replace(" ", "_")
                    extensions = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]
                    image_path = None

                    for ext in extensions:
                        test_path = os.path.join("Photos joueurs", "photos2", player_image_base + ext)
                        if os.path.exists(test_path):
                            image_path = test_path
                            break

                    if image_path:
                        with open(image_path, "rb") as f:
                            img_bytes = f.read()
                            encoded = base64.b64encode(img_bytes).decode()
                            img_html = f"""
                            <div style='display: flex; flex-direction: column; align-items: center;'>
                                <img src='data:image/jpeg;base64,{encoded}' 
                                    style='max-width: 180px; border-radius: 12px; margin-bottom: 0.5rem;' />
                                <p style='font-weight: bold; text-align: center;'>{selected_player}</p>
                            </div>
                            """
                            st_html(img_html, height=300)
                    else:
                        st.info("📸 Aucune photo disponible")

                with col_desc:
                    st.write(f"**Birthdate :** {infos.get('birthdate', 'N/A')}")
                    st.write(f"**Country :** {infos.get('country', 'N/A')}")
                    st.write(f"**Height :** {infos.get('height', 'N/A')}")
                    st.write(f"**Weight :** {infos.get('weight', 'N/A')}")
                    st.write(f"**Position :** {infos.get('position', 'N/A')}")
                    st.write(f"**Team :** {infos.get('team_name', 'N/A')}")




            def gauge(label, value, max_value, suffix=""):
                filled = int((value / max_value) * 100) if max_value > 0 else 0
                bar = f"""
                <div style='margin-bottom: 10px'>
                    <div style='font-weight: bold; font-size: 15px;'>{label}</div>
                    <div style='background-color:#c95d2e; border-radius:50px; overflow:hidden; height:28px; width:100%;'>
                        <div style='width:{filled}%; background-color:#501f17; height:100%; border-radius:50px;'></div>
                    </div>
                    <div style='text-align:right; font-style: italic; margin-top:2px;'>{round(value*100 if 'pct' in label else value,2)}{suffix}</div>
                </div>
                """
                st.markdown(bar, unsafe_allow_html=True)

            col_gauche, col_droite = st.columns(2)

            with col_gauche:
                gauge("Net Rating", infos.get("net_rating", 0), 30, "")
                gauge("True Shooting % (TS%)", infos.get("ts_pct", 0), 1, "%")
                gauge("Rebonds défensifs (%)", infos.get("dreb_pct", 0), 1, "%")

            with col_droite:
                gauge("Usage Rate (USG%)", infos.get("usg_pct", 0), 1, "%")
                gauge("Rebonds offensifs (%)", infos.get("oreb_pct", 0), 1, "%")
                gauge("Assists (%)", infos.get("ast_pct", 0), 1, "%")

        else:
            st.warning("❌ Infos non trouvées pour ce joueur")   




with tab2:
    st.title("📊 Statistiques globales de l'équipe")

    if not dream_team.empty:
        import plotly.express as px
        import plotly.graph_objects as go

        stats_somme = {
            "Total Points": dream_team["pts_per_game"].sum(),
            "Total Assists": dream_team["ast_per_game"].sum(),
            "Total Rebounds": dream_team["reb_per_game"].sum(),
            "REB% (sum)": dream_team["reb_pct_sum"].sum()
        }

        stats_moyenne = {
            "OREB%": dream_team["oreb_pct"].mean(),
            "DREB%": dream_team["dreb_pct"].mean(),
            "True Shooting %": dream_team["ts_pct"].mean(),
            "USG%": dream_team["usg_pct"].mean(),
            "AST%": dream_team["ast_pct"].mean(),
            "AST/USG Ratio": dream_team["ast_usg_ratio"].mean(),
            "Net Rating": dream_team["net_rating"].mean()
        }

        groupes = {
            "⚔️ Attaque": {
                "color": "#e74c3c",
                "somme": ["Total Points", "Total Assists"],
                "moyenne": ["USG%", "AST%", "AST/USG Ratio"]
            },
            "🧱 Rebonds": {
                "color": "#3498db",
                "somme": ["Total Rebounds", "REB% (sum)"],
                "moyenne": ["OREB%", "DREB%"]
            },
            "🎯 Efficacité & Ratios": {
                "color": "#2ecc71",
                "moyenne": ["Net Rating"]
            }
        }

        predicted_win = dream_team["predicted_win_rate"].mean() if "predicted_win_rate" in dream_team.columns else None

        # Removed the metric display block to avoid empty banner

        # ---------- LIGNE 1 : Efficacité & Chance ----------
        col1, col2, col3, col4 = st.columns([3,3,3,3], gap="large")

        # --- Carte Efficacité (sans True Shooting %) ---
        # Remove "True Shooting %" from moyenne list
        eff_stats = [stat for stat in groupes["🎯 Efficacité & Ratios"]["moyenne"] if stat != "True Shooting %"]
        df_eff = pd.DataFrame({
            "Stat": eff_stats,
            "Valeur": [stats_moyenne[k] for k in eff_stats]
        })
        fig_eff = px.bar(
            df_eff, x="Stat", y="Valeur", text="Valeur",
            template="plotly_white", height=300,
            color_discrete_sequence=[groupes["🎯 Efficacité & Ratios"]["color"]]
        )
        fig_eff.update_traces(marker_line_width=1, marker_line_color="white")
        fig_eff.update_layout(margin=dict(t=20, b=20, l=20, r=20), yaxis=dict(showgrid=False), xaxis_title="")

        with col1:
            st.markdown(f"""
            <div class='card'>
            <h3 style='color:{groupes["🎯 Efficacité & Ratios"]["color"]}; margin-bottom: 1rem'>
                🎯 Efficacité & Ratios
            </h3>
            </div>
            """, unsafe_allow_html=True)

            st_html(fig_eff.to_html(full_html=False, include_plotlyjs='cdn'), height=300)

            with st.expander("💡 Explication"):
                st.markdown("""
                Le Net Rating correspond à la différence entre les points marqués et les points encaissés pour 100 possessions.  
                Il reflète l'efficacité globale d’une équipe sur le terrain.
                """)





        # --- True Shooting % en donut ---
        ts_pct = stats_moyenne["True Shooting %"]
        fig_ts = go.Figure(data=[go.Pie(
            values=[ts_pct, 1 - ts_pct], hole=0.6,
            marker_colors=[groupes["🎯 Efficacité & Ratios"]["color"], "#ecf0f1"],
            textinfo="none"
        )])
        fig_ts.update_layout(
            showlegend=False,
            annotations=[{"text": f"{round(ts_pct*100,1)}%", "font": {"size": 28}, "showarrow": False}],
            template="plotly_white",
            margin=dict(t=20, b=20, l=20, r=20),
            height=300,
        )
        with col2:
            st.markdown(f"""
            <div class='card'>
            <h3 style='color:#2ecc71; margin-bottom: 1rem'>🎯 True Shooting %</h3>
            </div>
            """, unsafe_allow_html=True)
            st_html(fig_ts.to_html(full_html=False, include_plotlyjs='cdn'), height=300)
            with st.expander("💡 Explication"):
                st.markdown("""Le True Shooting % mesure l'efficacité au tir en tenant compte des tirs à 3 pts et des lancers francs.""")



        # --- Net Rating barre verticale ---
        # (Block removed to prevent duplicate green bar in tab2)

        # --- Carte Chance Moyenne ---
        primary = "#8e44ad"
        fig_donut = go.Figure(data=[go.Pie(
            values=[predicted_win, 1 - predicted_win], hole=0.6,
            marker_colors=[primary, "#ecf0f1"], textinfo="none"
        )])
        fig_donut.update_layout(
            showlegend=False,
            annotations=[{"text": f"{round(predicted_win*100,1)}%", "font": {"size": 28}, "showarrow": False}],
            template="plotly_white",
            margin=dict(t=20, b=20, l=20, r=20),
            height=300,
        )

        with col4:
            st.markdown(f"""
            <div class='card'>
            <h3 style='color:#8e44ad; margin-bottom: 1rem'>🔮 Chance Moyenne</h3>
            </div>
            """, unsafe_allow_html=True)
            st_html(fig_donut.to_html(full_html=False, include_plotlyjs='cdn'), height=300)
            with st.expander("💡 Explication"):
                st.markdown("""Probabilité moyenne de victoire calculée par le modèle sur la base des joueurs sélectionnés.""")



        # ---------- LIGNE 2 : Attaque & Rebonds ----------
        col5, col6, col7, col8 = st.columns(4, gap="large")

        # --- Total Points barre verticale ---
        fig_pts = px.bar(x=["Total Points"], y=[stats_somme["Total Points"]], text=[round(stats_somme["Total Points"],2)],
                         template="plotly_white", height=250, color_discrete_sequence=["#e74c3c"])
        fig_pts.update_traces(marker_line_width=1, marker_line_color="white")
        fig_pts.update_layout(margin=dict(t=20, b=20, l=20, r=20), yaxis=dict(showgrid=False), xaxis_title="")
        with col5:
            st.markdown(f"""
            <div class='card'>
            <h3 style='color:#e74c3c; margin-bottom: 1rem'>⚔️ Total Points</h3>
            </div>
            """, unsafe_allow_html=True)
            st_html(fig_pts.to_html(full_html=False, include_plotlyjs='cdn'), height=300)
            with st.expander("💡 Explication"):
                st.markdown("""Nombre total de points cumulés par les 5 joueurs de l’équipe.""")



        # --- Total Assists barre verticale ---
        fig_ast = px.bar(x=["Total Assists"], y=[stats_somme["Total Assists"]], text=[round(stats_somme["Total Assists"],2)],
                         template="plotly_white", height=250, color_discrete_sequence=["#e74c3c"])
        fig_ast.update_traces(marker_line_width=1, marker_line_color="white")
        fig_ast.update_layout(margin=dict(t=20, b=20, l=20, r=20), yaxis=dict(showgrid=False), xaxis_title="")
        with col6:
            st.markdown(f"""
            <div class='card'>
            <h3 style='color:#e74c3c; margin-bottom: 1rem'>⚔️ Total Assists</h3>
            </div>
            """, unsafe_allow_html=True)
            st_html(fig_ast.to_html(full_html=False, include_plotlyjs='cdn'), height=300)
            with st.expander("💡 Explication"):
                st.markdown("""Nombre total de passes décisives réalisées par les 5 joueurs.""")



        # --- USG% et AST% barres horizontales ---
        df_usg_ast = pd.DataFrame({
            "Stat": ["USG%", "AST%"],
            "Valeur": [stats_moyenne["USG%"], stats_moyenne["AST%"]]
        })
        fig_usg_ast = px.bar(df_usg_ast, y="Stat", x="Valeur", orientation="h", text="Valeur",
                             template="plotly_white", height=250,
                             color_discrete_sequence=["#e74c3c", "#e74c3c"])
        fig_usg_ast.update_traces(marker_line_width=1, marker_line_color="white")
        fig_usg_ast.update_layout(margin=dict(t=20, b=20, l=20, r=20), xaxis=dict(showgrid=False), yaxis_title="")
        with col7:
            st.markdown(f"""
            <div class='card'>
            <h3 style='color:#e74c3c; margin-bottom: 1rem'>⚔️ Usage & Assists %</h3>
            </div>
            """, unsafe_allow_html=True)
            st_html(fig_usg_ast.to_html(full_html=False, include_plotlyjs='cdn'), height=300)
            with st.expander("💡 Explication"):
                st.markdown("""USG% mesure l'implication d'un joueur dans les possessions offensives. AST% indique la proportion de passes menant à un panier.""")



        # --- AST/USG Ratio chiffre centré ---
        ratio_val = stats_moyenne["AST/USG Ratio"]
        with col8:
            st.markdown(f"""
            <div class='card'>
            <h3 style='color:#e74c3c; margin-bottom: 1rem'>⚔️ AST/USG Ratio</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 48px; font-weight: bold; text-align: center;'>{round(ratio_val, 2)}</div>", unsafe_allow_html=True)
            with st.expander("💡 Explication"):
                st.markdown("""Ratio entre le pourcentage de passes décisives et le pourcentage d'utilisation. Il indique l'efficacité collective dans le jeu offensif.""")



        # ---------- LIGNE 3 : Rebonds ----------
        col9, col10, col11, col12 = st.columns(4, gap="large")

        # --- Total Rebounds barre verticale ---
        fig_reb = px.bar(x=["Total Rebounds"], y=[stats_somme["Total Rebounds"]], text=[round(stats_somme["Total Rebounds"],2)],
                         template="plotly_white", height=250, color_discrete_sequence=[groupes["🧱 Rebonds"]["color"]])
        fig_reb.update_traces(marker_line_width=1, marker_line_color="white")
        fig_reb.update_layout(margin=dict(t=20, b=20, l=20, r=20), yaxis=dict(showgrid=False), xaxis_title="")
        with col9:
            st.markdown(f"""
            <div class='card'>
            <h3 style='color:#3498db; margin-bottom: 1rem'>🧱 Total Rebounds</h3>
            </div>
            """, unsafe_allow_html=True)
            st_html(fig_reb.to_html(full_html=False, include_plotlyjs='cdn'), height=300)
            with st.expander("💡 Explication"):
                st.markdown("""Nombre total de rebonds cumulés par l’équipe (offensifs + défensifs).""")



        # --- REB% (sum) donut ---
        reb_pct_sum = stats_somme["REB% (sum)"]
        fig_reb_pct = go.Figure(data=[go.Pie(
            values=[reb_pct_sum, 1 - reb_pct_sum], hole=0.6,
            marker_colors=[groupes["🧱 Rebonds"]["color"], "#ecf0f1"],
            textinfo="none"
        )])
        fig_reb_pct.update_layout(
            showlegend=False,
            annotations=[{"text": f"{round(reb_pct_sum*100,1)}%", "font": {"size": 28}, "showarrow": False}],
            template="plotly_white",
            margin=dict(t=20, b=20, l=20, r=20),
            height=300,
        )
        with col10:
            st.markdown(f"""
            <div class='card'>
            <h3 style='color:#3498db; margin-bottom: 1rem'>🧱 REB% (sum)</h3>
            </div>
            """, unsafe_allow_html=True)
            st_html(fig_reb_pct.to_html(full_html=False, include_plotlyjs='cdn'), height=300)
            with st.expander("💡 Explication"):
                st.markdown("""Pourcentage combiné de rebonds pris par l’équipe par rapport aux rebonds disponibles.""")



        # --- OREB% et DREB% barres horizontales ---
        df_oreb_dreb = pd.DataFrame({
            "Stat": ["OREB%", "DREB%"],
            "Valeur": [stats_moyenne["OREB%"], stats_moyenne["DREB%"]]
        })
        fig_oreb_dreb = px.bar(df_oreb_dreb, y="Stat", x="Valeur", orientation="h", text="Valeur",
                               template="plotly_white", height=250,
                               color_discrete_sequence=[groupes["🧱 Rebonds"]["color"], groupes["🧱 Rebonds"]["color"]])
        fig_oreb_dreb.update_traces(marker_line_width=1, marker_line_color="white")
        fig_oreb_dreb.update_layout(margin=dict(t=20, b=20, l=20, r=20), xaxis=dict(showgrid=False), yaxis_title="")
        with col11:
            st.markdown(f"""
            <div class='card'>
            <h3 style='color:#3498db; margin-bottom: 1rem'>🧱 Offensive & Defensive Rebounds %</h3>
            </div>
            """, unsafe_allow_html=True)
            st_html(fig_oreb_dreb.to_html(full_html=False, include_plotlyjs='cdn'), height=300)
            with st.expander("💡 Explication"):
                st.markdown("""Pourcentages moyens de rebonds offensifs et défensifs captés par les joueurs.""")



        # Empty column for layout balance
        with col12:
            st.write("")

    else:
        st.warning("Aucune équipe sélectionnée.")
        