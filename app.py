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
        footer {visibility: hidden;}
        #stDecoration {display:none;}
        /* 1. 隐藏右下角的 Streamlit 徽章 */
        [data-testid="stViewerBadge"] {
            display: none !important;
        }

        /* 2. 隐藏底部的 "Made with Streamlit" 脚注 */
        footer {
            visibility: hidden;
        }

        /* 3. 隐藏顶部的装饰线和菜单 */
        header {
            visibility: hidden;
        }
        #MainMenu {
            visibility: hidden;
        }
        .stDeployButton {
            display: none;
        }
        
        /* 4. 移除多余的边距，让页面更紧凑 */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 0rem;
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
