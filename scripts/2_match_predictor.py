import streamlit as st
import pandas as pd
from models.lineup_predictor import LineupPredictor
import random

# ---------- 1) Charger le predictor (cache mémoire) ----------
@st.cache_resource
def load_predictor() -> LineupPredictor:
    lp = LineupPredictor()
    lp.load_data()          # lit les CSV, entraîne le modèle
    return lp

lp = load_predictor()

@st.cache_data
def load_prefab_teams():
    return pd.read_csv("Data final/player_team_statistics.csv", sep=";")

@st.cache_data
def load_team_level_stats():
    # adapte le chemin + séparateur si besoin
    return pd.read_csv(
        "Data final/nba_team_statistics_final_without_players.csv" \
        "",  # <‑ ton CSV d’équipes
        sep=";"                                                  # ; si ton fichier est séparé par ;
    )


# ---------- 2) Interface ----------
st.title("Line-Up Predictor")

tab_custom, tab_prefab = st.tabs(
    ["🎯 Choisis 2×5 joueurs", "🚀 Équipes existantes"]
)

# ---------- 2.b Mode custom ----------
with tab_custom:
    st.subheader("Compose tes équipes")
    all_players = sorted(lp.players_data["player_name"].unique())

    colA, colB = st.columns(2)

    with colA:
        st.subheader("Équipe A")
        if st.button("🔀 Aléatoire A"):
            st.session_state.teamA = random.sample(all_players, 5)
        players_A = st.multiselect("Choisis 5 joueurs",
                                   all_players, key="teamA")

    with colB:
        st.subheader("Équipe B")
        if st.button("🔀 Aléatoire B"):
            st.session_state.teamB = random.sample(all_players, 5)
        players_B = st.multiselect("Choisis 5 joueurs",
                                   all_players, key="teamB")


    if st.button("Prédire le vainqueur", key="btn_custom"):
        if len(players_A) != 5 or len(players_B) != 5:
            st.error("❗ Sélectionne exactement 5 joueurs dans chaque équipe.")
        else:
            dfA = lp.players_data[lp.players_data.player_name.isin(players_A)]
            dfB = lp.players_data[lp.players_data.player_name.isin(players_B)]

            # Transforme DataFrame → liste de dicts (format attendu)
            def df_to_lineup(df):
                return [{
                    "position": r["primary_pos"],
                    "team":     r["team_abbreviation"],
                    "name":     r["player_name"],
                    "stats":    {k: r[k] for k in lp.features},
                } for _, r in df.iterrows()]

            lineupA = df_to_lineup(dfA)
            lineupB = df_to_lineup(dfB)

            winner, w_score, l_score, w_desc, l_desc = lp.predict_winner(
                lineupA, lineupB)

            # --- Affichage des probabilités propres ---
            if winner == lineupA:
                st.success(f"🏆 Victoire la plus probable : **Équipe A** ({w_score*100:.1f} %)")
                st.info   (f"Probabilité Équipe B : {l_score*100:.1f} %")
            else:
                st.success(f"🏆 Victoire la plus probable : **Équipe B** ({w_score*100:.1f} %)")
                st.info   (f"Probabilité Équipe A : {l_score*100:.1f} %")
            
            # --------------------------------------------------
        # Donut de probabilité
        # --------------------------------------------------
        import plotly.graph_objects as go, plotly.express as px, pandas as pd

        # -------- Donuts pour chaque équipe A (rouge) et B (bleu)
        col_a, col_b = st.columns(2)

        with col_a:
            donutA = go.Figure(go.Pie(
                values=[w_score if winner is lineupA else l_score, 1 - (w_score if winner is lineupA else l_score)],
                labels=["Victoire", "Défaite"],
                hole=0.55,
                marker_colors=["#e74c3c", "#ecf0f1"],
                textinfo="none"
            ))
            donutA.update_layout(
                title="Équipe A",
                showlegend=False,
                annotations=[dict(text=f"{(w_score if winner is lineupA else l_score)*100:.1f}%", font_size=24, showarrow=False)]
            )
            st.plotly_chart(donutA, use_container_width=True)

        with col_b:
            donutB = go.Figure(go.Pie(
                values=[l_score if winner is lineupA else w_score, 1 - (l_score if winner is lineupA else w_score)],
                labels=["Victoire", "Défaite"],
                hole=0.55,
                marker_colors=["#3498db", "#ecf0f1"],
                textinfo="none"
            ))
            donutB.update_layout(
                title="Équipe B",
                showlegend=False,
                annotations=[dict(text=f"{(l_score if winner is lineupA else w_score)*100:.1f}%", font_size=24, showarrow=False)]
            )
            st.plotly_chart(donutB, use_container_width=True)

        # --------------------------------------------------
        # Barres rouge / bleu (stats agrégées à partir des 5 joueurs)
        # --------------------------------------------------
        def aggregate(df):
            return {
                "Total Points":      df["pts_per_game"].sum(),
                "Total Assists":     df["ast_per_game"].sum(),
                "Total Rebounds":    df["reb_per_game"].sum(),
                "REB% (sum)":        df["reb_pct_sum"].sum(),
                "OREB%":             df["oreb_pct"].mean(),
                "DREB%":             df["dreb_pct"].mean(),
                "True Shooting %":   df["ts_pct"].mean(),
                "USG%":              df["usg_pct"].mean(),
                "AST%":              df["ast_pct"].mean(),
                "AST/USG Ratio":     df["ast_usg_ratio"].mean(),
                "Net Rating":        df["net_rating"].mean(),
            }

        statsA, statsB = aggregate(dfA), aggregate(dfB)

        col_usg, col_ratio = st.columns([3, 1])

        with col_usg:
            df_usg_ast = pd.DataFrame({
                "Stat": ["USG%", "AST%"] * 2,
                "Équipe": ["A"] * 2 + ["B"] * 2,
                "Valeur": [
                    statsA["USG%"], statsA["AST%"],
                    statsB["USG%"], statsB["AST%"]
                ]
            })

            fig_usg_ast = px.bar(df_usg_ast, x="Valeur", y="Stat", color="Équipe",
                                orientation="h", barmode="group",
                                color_discrete_map={"A": "#e74c3c", "B": "#3498db"},
                                text_auto=".2f", height=300)

            fig_usg_ast.update_layout(
                title="Usage % & Assists %",
                xaxis=dict(showgrid=False),
                yaxis_title=None,
                xaxis_title=None
            )

            st.plotly_chart(fig_usg_ast, use_container_width=True)

            with st.expander("💡 Explication"):
                st.markdown("""
                - **USG%** mesure l'implication d’un joueur dans les possessions offensives (tirs, fautes, balles perdues).
                - **AST%** mesure le pourcentage des paniers d'équipe qui proviennent d'une passe du joueur.
                """)

        with col_ratio:
            ratio_a = statsA["AST%"] / statsA["USG%"] if statsA["USG%"] > 0 else 0
            ratio_b = statsB["AST%"] / statsB["USG%"] if statsB["USG%"] > 0 else 0

            st.markdown("### ⚖️ AST/USG Ratio", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='text-align:center; font-size:22px; font-weight:bold; color:#e74c3c'>Équipe A : {ratio_a:.2f}</div>
            <div style='text-align:center; font-size:22px; font-weight:bold; color:#3498db'>Équipe B : {ratio_b:.2f}</div>
            """, unsafe_allow_html=True)

            with st.expander("💡 Explication"):
                st.markdown("""
                Ce ratio compare la capacité de passes décisives à l'implication offensive.  
                Un ratio élevé peut indiquer un jeu collectif plus efficace.
                """)


        col_pts, col_ast = st.columns(2)

        with col_pts:
            fig_pts = px.bar(
                x=["Équipe A", "Équipe B"],
                y=[statsA["Total Points"], statsB["Total Points"]],
                color=["A", "B"],
                text=[round(statsA["Total Points"], 2), round(statsB["Total Points"], 2)],
                color_discrete_map={"A": "#e74c3c", "B": "#3498db"},
                template="plotly_white", height=250
            )
            fig_pts.update_layout(title="🏀 Total Points", showlegend=False)
            st.plotly_chart(fig_pts, use_container_width=True)

            with st.expander("💡 Explication"):
                st.markdown("Total des points marqués par les 5 joueurs sélectionnés de chaque équipe.")

        with col_ast:
            fig_ast = px.bar(
                x=["Équipe A", "Équipe B"],
                y=[statsA["Total Assists"], statsB["Total Assists"]],
                color=["A", "B"],
                text=[round(statsA["Total Assists"], 2), round(statsB["Total Assists"], 2)],
                color_discrete_map={"A": "#e74c3c", "B": "#3498db"},
                template="plotly_white", height=250
            )
            fig_ast.update_layout(title="🎯 Total Assists", showlegend=False)
            st.plotly_chart(fig_ast, use_container_width=True)

            with st.expander("💡 Explication"):
                st.markdown("Nombre total de passes décisives faites par les 5 joueurs sélectionnés.")


        cols_off = ["Total Points", "Total Assists"]  # AST%, USG% retirés
        cols_eff  = ["True Shooting %", "Net Rating"]
        cols_reb  = ["Total Rebounds", "REB% (sum)", "OREB%", "DREB%"]






        def make_bar_section(title, cols):
            plot_df = pd.DataFrame(
                [{"Stat": c, "Valeur": statsA[c], "Équipe": "A"} for c in cols] +
                [{"Stat": c, "Valeur": statsB[c], "Équipe": "B"} for c in cols])
            fig = px.bar(plot_df, x="Stat", y="Valeur", color="Équipe",
                         barmode="group",
                         color_discrete_map={"A": "#e74c3c", "B": "#3498db"},
                         text_auto=".2f", height=350)
            fig.update_layout(xaxis_tickangle=-45, title=title)
            st.plotly_chart(fig, use_container_width=True)


        # --- True Shooting % ---
        fig_ts = px.bar(
            x=["Équipe A", "Équipe B"],
            y=[statsA["True Shooting %"], statsB["True Shooting %"]],
            color=["A", "B"],
            text=[round(statsA["True Shooting %"], 2), round(statsB["True Shooting %"], 2)],
            color_discrete_map={"A": "#e74c3c", "B": "#3498db"},
            template="plotly_white", height=250
        )
        fig_ts.update_layout(title="🎯 True Shooting %", showlegend=False)
        st.plotly_chart(fig_ts, use_container_width=True)
        with st.expander("💡 Explication"):
            st.markdown("Le **True Shooting %** mesure l'efficacité d’un joueur en tenant compte des tirs à 3 points et des lancers francs.")

        # --- Net Rating ---
        fig_net = px.bar(
            x=["Équipe A", "Équipe B"],
            y=[statsA["Net Rating"], statsB["Net Rating"]],
            color=["A", "B"],
            text=[round(statsA["Net Rating"], 2), round(statsB["Net Rating"], 2)],
            color_discrete_map={"A": "#e74c3c", "B": "#3498db"},
            template="plotly_white", height=250
        )
        fig_net.update_layout(title="📈 Net Rating", showlegend=False)
        st.plotly_chart(fig_net, use_container_width=True)
        with st.expander("💡 Explication"):
            st.markdown("Le **Net Rating** correspond à la différence entre les points marqués et encaissés pour 100 possessions.")

        # --- Total Rebounds ---
        fig_total_reb = px.bar(
            x=["Équipe A", "Équipe B"],
            y=[statsA["Total Rebounds"], statsB["Total Rebounds"]],
            color=["A", "B"],
            text=[round(statsA["Total Rebounds"], 2), round(statsB["Total Rebounds"], 2)],
            color_discrete_map={"A": "#e74c3c", "B": "#3498db"},
            template="plotly_white", height=250
        )
        fig_total_reb.update_layout(title="🧱 Total Rebounds", showlegend=False)
        st.plotly_chart(fig_total_reb, use_container_width=True)
        with st.expander("💡 Explication"):
            st.markdown("Nombre total de rebonds captés par l’équipe, toutes catégories confondues.")

        # --- REB% (sum) ---
        fig_reb_sum = px.bar(
            x=["Équipe A", "Équipe B"],
            y=[statsA["REB% (sum)"], statsB["REB% (sum)"]],
            color=["A", "B"],
            text=[round(statsA["REB% (sum)"], 2), round(statsB["REB% (sum)"], 2)],
            color_discrete_map={"A": "#e74c3c", "B": "#3498db"},
            template="plotly_white", height=250
        )
        fig_reb_sum.update_layout(title="📊 REB% (sum)", showlegend=False)
        st.plotly_chart(fig_reb_sum, use_container_width=True)
        with st.expander("💡 Explication"):
            st.markdown("Le **REB%** correspond au pourcentage de rebonds captés sur l’ensemble des rebonds disponibles.")

        # --- OREB% et DREB% ---
        df_oreb_dreb = pd.DataFrame({
            "Stat": ["OREB%", "DREB%"] * 2,
            "Équipe": ["A"] * 2 + ["B"] * 2,
            "Valeur": [
                statsA["OREB%"], statsA["DREB%"],
                statsB["OREB%"], statsB["DREB%"]
            ]
        })

        fig_oreb_dreb = px.bar(df_oreb_dreb, y="Stat", x="Valeur", color="Équipe",
                            orientation="h", barmode="group",
                            color_discrete_map={"A": "#e74c3c", "B": "#3498db"},
                            text_auto=".2f", height=250)
        fig_oreb_dreb.update_layout(title="🧱 Offensive & Defensive Rebounds %", showlegend=True)
        st.plotly_chart(fig_oreb_dreb, use_container_width=True)
        with st.expander("💡 Explication"):
            st.markdown("""
            - **OREB%** : rebonds offensifs captés / rebonds offensifs disponibles  
            - **DREB%** : rebonds défensifs captés / rebonds défensifs disponibles
            """)



















# ---------- Mode équipes existantes ----------
with tab_prefab:
    st.subheader("Compare deux équipes déjà constituées")

    df_prefab = load_prefab_teams()
    if "team_name" not in df_prefab.columns:
        st.error("❗ Le CSV doit contenir la colonne 'team_name'")
        st.stop()

    team_names = sorted(df_prefab["team_name"].unique())
    col1, col2 = st.columns(2)
    with col1:
        teamA_name = st.selectbox("Équipe A", team_names, key="prefA")
    with col2:
        teamB_name = st.selectbox("Équipe B", team_names, key="prefB")

    # -- bouton --
    if st.button("Prédire le vainqueur (équipes existantes)"):
        # ------------------------- helpers -------------------------
        def team_lineup(df, team_name, k=5):
            if "pts_per_game" in df.columns:
                subset = df[df.team_name == team_name].copy()
                return subset.nlargest(k, "pts_per_game")
            return df[df.team_name == team_name].sample(k, random_state=42)

        def df_to_lineup(df):
            return [{
                "position": None,
                "team":     row["team_abbreviation"],
                "name":     row["player_name"],
                "stats":    {k: row.get(k, 0) for k in lp.features},
            } for _, row in df.iterrows()]
        # -----------------------------------------------------------

        dfA, dfB   = team_lineup(df_prefab, teamA_name), team_lineup(df_prefab, teamB_name)
        lineupA    = df_to_lineup(dfA)
        lineupB    = df_to_lineup(dfB)
        winner, w_score, l_score, w_desc, l_desc = lp.predict_winner(lineupA, lineupB)

        if winner == lineupA:
            st.success(f"🏆 Victoire la plus probable : **{teamA_name}** ({w_score*100:.1f} %)")
            st.info   (f"Probabilité {teamB_name} : {l_score*100:.1f} %")
        else:
            st.success(f"🏆 Victoire la plus probable : **{teamB_name}** ({w_score*100:.1f} %)")
            st.info   (f"Probabilité {teamA_name} : {l_score*100:.1f} %")

        # ------------------------------------------------------------------
        # SECTION : Graphiques basés sur le CSV 'team_level'
        # ------------------------------------------------------------------
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go

        # ---------- Glossaire + helper graphique + expander ---------------
        EXPLAIN = {
            "ppg":        "PPG = **Points** marqués en moyenne par match.",
            "apg":        "APG = **Passes décisives** distribuées par match.",
            "fg_pct":     "FG % = % de **tirs (2 pts + 3 pts)** réussis.",
            "fg3_pct":    "3P % = % de **tirs à 3 points** réussis.",
            "ft_pct":     "FT % = % de **lancers francs** réussis.",
            "net_rating": "Net Rating = points marqués − points encaissés pour 100 possessions.",
            "opp_ppg":    "Opp PPG = points encaissés en moyenne par match.",
            "tov_pg":     "TOV PG = balles perdues en moyenne par match.",
            "rpg":        "RPG = rebonds captés (off + def) par match.",
            "spg":        "SPG = interceptions en moyenne par match.",
            "bpg":        "BPG = contres en moyenne par match."
        }

        def show_chart_with_expander(fig, stat_cols, title="💡 Explication"):
            st.plotly_chart(fig, use_container_width=True)
            if isinstance(stat_cols, str):
                stat_cols = [stat_cols]
            bullets = "\n".join(f"* {EXPLAIN.get(c, c)}" for c in stat_cols)
            with st.expander(title):
                st.markdown(bullets)

        # ---------- data & couleurs ----------
        df_teamlvl = load_team_level_stats()
        rowA = df_teamlvl[df_teamlvl.team_name == teamA_name].iloc[0]
        rowB = df_teamlvl[df_teamlvl.team_name == teamB_name].iloc[0]
        color_map = {teamA_name: "#e74c3c", teamB_name: "#3498db"}

        # ---------- donuts ----------
        def donut_chart(prob, title, color):
            fig = go.Figure(go.Pie(values=[prob, 1-prob], labels=["Victoire", "Défaite"],
                                   hole=.55, marker_colors=[color, "#ecf0f1"], textinfo="none"))
            fig.update_layout(title=title, showlegend=False,
                              annotations=[dict(text=f"{prob*100:.1f} %", font_size=24, showarrow=False)])
            return fig
        probA, probB = (w_score, l_score) if winner == lineupA else (l_score, w_score)
        col_donA, col_donB = st.columns(2)
        with col_donA:
            st.plotly_chart(donut_chart(probA, f"Probabilité {teamA_name}", "#e74c3c"), use_container_width=True)
        with col_donB:
            st.plotly_chart(donut_chart(probB, f"Probabilité {teamB_name}", "#3498db"), use_container_width=True)

        # ---------- helpers bar charts ----------
        def bar_single_stat(stat_col, title):
            df_b = pd.DataFrame({"Équipe": [teamA_name, teamB_name],
                                 "Valeur": [rowA.get(stat_col, 0), rowB.get(stat_col, 0)]})
            fig = px.bar(df_b, x="Équipe", y="Valeur", color="Équipe", text_auto=".2f",
                         color_discrete_map=color_map, height=350)
            fig.update_layout(title=title, showlegend=False)
            return fig

        def bar_multi_horizontal(stat_cols, title):
            df_b = pd.DataFrame(
                [{"Stat": c, "Valeur": rowA.get(c, 0), "Équipe": teamA_name} for c in stat_cols] +
                [{"Stat": c, "Valeur": rowB.get(c, 0), "Équipe": teamB_name} for c in stat_cols]
            )
            fig = px.bar(df_b, x="Valeur", y="Stat", orientation="h",
                         color="Équipe", barmode="group", text_auto=".2f",
                         color_discrete_map=color_map, height=350)
            fig.update_layout(title=title)
            return fig

        # -------------------- OFFENSE -------------------- #
        st.markdown("### 🏀 Attaque – Totaux")
        # Regrouper PPG, APG, FG% dans la même ligne
        cols1 = st.columns(3)
        with cols1[0]:
            show_chart_with_expander(bar_single_stat("ppg", "Points par match (PPG)"), "ppg")
        with cols1[1]:
            show_chart_with_expander(bar_single_stat("apg", "Passes déc. par match (APG)"), "apg")
        with cols1[2]:
            show_chart_with_expander(
                bar_multi_horizontal(["fg_pct", "fg3_pct", "ft_pct"],
                                     "Pourcentages : FG %, 3P %, FT %"),
                ["fg_pct", "fg3_pct", "ft_pct"]
            )

        # -------------------- EFFICACITÉ & RATIOS -------------------- #
        st.markdown("### ⚙️ Efficacité & Ratios")
        cols2 = st.columns(3)
        with cols2[0]:
            show_chart_with_expander(bar_single_stat("net_rating", "Net Rating"),  "net_rating")
        with cols2[1]:
            show_chart_with_expander(bar_single_stat("opp_ppg",   "Points encaissés (Opp PPG)"), "opp_ppg")
        with cols2[2]:
            show_chart_with_expander(bar_single_stat("tov_pg",    "Balles perdues (TOV PG)"),    "tov_pg")

        # -------------------- 🧱 Rebonds -------------------- #
        st.markdown("### 🧱 Rebonds & Défense")
        cols3 = st.columns(3)
        with cols3[0]:
            show_chart_with_expander(bar_single_stat("rpg", "Rebonds par match (RPG)"), "rpg")
        with cols3[1]:
            show_chart_with_expander(bar_single_stat("spg", "Interceptions par match (SPG)"), "spg")
        with cols3[2]:
            show_chart_with_expander(bar_single_stat("bpg", "Contres par match (BPG)"), "bpg")
