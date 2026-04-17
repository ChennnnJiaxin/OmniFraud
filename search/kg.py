import sys
import neo4j
import streamlit as st
from pyvis.network import Network
import os
import uuid

# ============================
# 颜色配置
# ============================
node_color_map = {
    "案件": "#FF6347",    # Tomato
    "人物": "#1E90FF",    # DodgerBlue
    "机构": "#20B2AA",    # LightSeaGreen
    "地点": "#3CB371",    # MediumSeaGreen
    "工具": "#FFA500",    # Orange
    "诈骗类型": "#BA55D3", # MediumOrchid
    "实体资产": "#FFD700", # Gold
    "罪名": "#A9A9A9",     # DarkGray
    "法律法规": "#CD853F"  # Peru
}

rel_color_map = {
    "涉及被害人": "#FF69B4",
    "涉及嫌疑人": "#00CED1",
    "属于组织": "#7B68EE",
    "所在地": "#32CD32",
    "案发地点": "#FF4500",
    "触犯法律法规": "#8B0000",
    "诈骗类型": "#9400D3",
    "涉案工具": "#FF8C00",
    "人物关系": "#4682B4",
    "涉案资产": "#9ACD32",
    "罪名": "#808080",
    "刑事判决": "#DC143C",
    "赔偿量": "#00FA9A",
    "赔偿给": "#00BFFF"
}

# ============================
# 数据库连接配置
# ============================
@st.cache_resource(ttl=120, show_spinner=False)
def connect_to_neo4j():
    """连接 Neo4j 数据库"""
    uri = st.session_state.neo4j_uri
    username = st.session_state.neo4j_username
    password = st.session_state.neo4j_password
    database = st.session_state.neo4j_database
    return neo4j.GraphDatabase.driver(uri, auth=(username, password), database=database)

# ============================
# 可视化函数
# ============================
def init_net():
    net = Network(
        directed=True,
        height="800px",
        width="100%",
        notebook=False,
        cdn_resources="remote"
    )
    
    # 生成可视化
    net.set_options("""
    {
        "physics": {
            "enabled": true,
            "stabilization": {
                "enabled": true,
                "iterations": 100
            },
            "timestep": 0.5,
            "adaptiveTimestep": true,
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 100,
                "springConstant": 0.08,
                "damping": 0.4,
                "avoidOverlap": 0.5
            }
        },
        "interaction": {
            "tooltipDelay": 200,
            "hideEdgesOnDrag": false,
            "hideNodesOnDrag": false
        }
    }
    """)
    return net

def visualize_case_network(case_name, net = None):
    driver = connect_to_neo4j()
    # 修改后的Cypher查询
    cypher_query = """
    MATCH (case:案件 {name: $case_name})
    OPTIONAL MATCH path=(case)-[rels*1..2]-(related)
    WHERE ALL(
        n IN nodes(path) 
        WHERE NOT n:案件 OR n = case
    )
    WITH case, 
         [n IN nodes(path) WHERE NOT n:案件] AS path_nodes,
         rels AS path_rels
    UNWIND (path_nodes + [case]) AS node
    UNWIND path_rels AS rel
    RETURN collect(DISTINCT node)[..100] AS nodes, 
           collect(DISTINCT rel)[..150] AS rels
    """
    
    with driver.session() as session:
        result = session.run(cypher_query, case_name=case_name)
        record = result.single()
        
        if not record or not record["nodes"]:
            st.warning("未找到相关案件信息")
            return

        if not net:
            net = init_net()
        
        # 添加节点（过滤content属性）
        seen_nodes = set()
        for node in record["nodes"]:
            node_id = node.element_id
            if node_id in seen_nodes:
                continue
            seen_nodes.add(node_id)
            
            labels = list(node.labels)
            node_type = labels[0] if labels else "其他"
            name = node.get("name", "未知名称")
            
            # 过滤content属性并格式化标题
            filtered_props = {
                k: v for k, v in node.items() 
                if k != "content" and not k.startswith("_")
            }
            title = "\n".join(
                [f"{k}: {v}" for k, v in filtered_props.items()]
            )
            
            color = node_color_map.get(node_type, "#888888")
            net.add_node(
                node_id,
                label=name,
                title=title,
                color=color,
                font={"size": 12}
            )

        # 添加关系
        seen_rels = set()
        for rel in record["rels"]:
            rel_id = rel.element_id
            if rel_id in seen_rels:
                continue
            seen_rels.add(rel_id)
            
            rel_type = rel.type
            source = rel.start_node.element_id
            target = rel.end_node.element_id
            
            # 设置关系颜色
            color = rel_color_map.get(rel_type, "#666666")
            
            net.add_edge(
                source,
                target,
                label=rel_type,
                color=color,
                width=1.5,
                arrows="to"
            )
        return net


def show_net(net, height=500):
    net.save_graph("temp.html")
    with open("temp.html", "r", encoding="utf-8") as f:
        html = f.read()
    st.components.v1.html(html, height=height)

@st.cache_data(ttl=120, show_spinner=False)
@st.dialog("案件详情", width="large")
def show_case_detail(case_name):
    cypher_query = """
    MATCH (case:案件 {name: $case_name})
    RETURN case
    """
    driver = connect_to_neo4j()
    with st.spinner("载入案件详情……"):
        with driver.session() as session:
            result = session.run(cypher_query, case_name=case_name)
            record = result.single()
            if record:
                case = record["case"]
                st.write(f"案件名称: {case['name']}")
                st.write(f"案件描述: {case['description']}")
                with st.expander("查看判决书", expanded=False):
                    st.write(case.get("content", "无判决书信息"))
                with st.spinner("载入知识图谱……"):
                    net = visualize_case_network(case_name)
                    show_net(net, height=500)
                # st.write(f"案件类型: {', '.join(case.get('types', []))}")
                # st.write(f"案件子类型: {', '.join(case.get('subtypes', []))}")
                # st.write(f"案件嫌疑人: {', '.join(case.get('suspects', []))}")
                # st.write(f"案件被害人: {', '.join(case.get('victims', []))}")
            else:
                st.warning("未找到相关案件信息")
            
    

# ============================
# Streamlit 界面
# ============================
# if __name__ == "__streamlit__":
# st.title("反诈骗案件知识图谱可视化")
# case_name = st.text_input("请输入案件名称：", key="case_name")

# if case_name:
#     st.write(f"正在可视化案件：{case_name}")
#     net = visualize_case_network(case_name)
#     if net:
#         st.write("案件知识图谱：")
#         show_net(net)
#     else:
#         st.warning("未找到相关案件信息")
# else:
#     st.info("请在上方输入框输入案件名称")