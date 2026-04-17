import streamlit as st

st.set_page_config(
    page_title="OmniFraud",
    layout="wide",
    page_icon="assets/logo.png",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
        [data-testid="stToolbar"] {display: none !important;}
        [data-testid="stStatusWidget"] {display: none !important;}
        [data-testid="stAppViewContainer"] > .main .block-container {
            padding-top: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

st.session_state.neo4j_uri = st.secrets['NEO4J_URI']
st.session_state.neo4j_username = st.secrets['NEO4J_USERNAME']
st.session_state.neo4j_database = st.secrets['NEO4J_DATABASE']
st.session_state.neo4j_password = st.secrets['NEO4J_PASSWORD']

st.logo("assets/OmniFraud2.png", size="large", icon_image="assets/OmniFraud2.png")

start_page = st.Page("start_page.py", title="欢迎", icon="🎉")
recognize_page = st.Page('recognize_page.py', title='短信识别', icon='📩')
bot_page = st.Page('bot_page.py', title='问答助手', icon='🤖')
risk_page = st.Page("risk_page.py", title="风险评估", icon="📊")
search_page = st.Page('search_page.py', title='案件搜索', icon='🔍')
show_page = st.Page('show_page.py', title='反诈警示', icon='📰')

pages = [start_page, recognize_page, bot_page, risk_page, search_page, show_page]
pg = st.navigation(pages)
pg.run()
