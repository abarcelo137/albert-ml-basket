import streamlit as st
import base64
import pathlib

def set_bg(png_file: str, size: str = "contain"):
    """
    Ajoute une image PNG en fond d'écran de l'app Streamlit.
    - png_file : chemin relatif ou absolu vers l'image
    - size     : 'cover', 'contain', '50%', etc.
    """
    file_path = pathlib.Path(png_file)
    if not file_path.exists():
        st.error(f"Image '{png_file}' introuvable")
        return

    with open(png_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)), url("data:image/png;base64,{encoded}");
            background-size  : {size};
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


st.set_page_config(page_title="NBA Dashboard", layout="wide")

set_bg("assets/background.png", size="cover")

st.markdown(
    """
    <style>
    .block-container{
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        min-height:100vh;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align:center; font-family:Anton; margin-top:0; color:#ffd230;'>Optimisation des équipes NBA</h1>", unsafe_allow_html=True)

# Tu n'as rien d'autre à coder ici : la navigation se fait grâce au dossier 'pages'
