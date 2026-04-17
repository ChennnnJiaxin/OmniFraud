import streamlit as st
from ..llm import llm
from ..graph import graph



# Create the Cypher QA chain
from langchain_neo4j import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about Fraud cases.
Convert the user's question based on the schema.

Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Do not return entire nodes or embedding properties.

Fine Tuning:

- Cypher 代码中，所有实体与关系按照给定的 Schema 定义，不要翻译中英文。
- 尽量只返回所需的信息，不要返回整个节点或关系。
- 如果需要概述性的回答问题，可以返回某个节点的 `description` 属性。
- 当需要列出结点（如案例、人物、机构等）时，需要使用 `LIMIT` 限制返回结果的数量。最多返回 8 个案例即可。
- 当需要举例时，如果结点具有 `name` 和 `description` 属性，可以返回这两个属性。
- 请确保 Cypher 代码的正确性，不要包含语法错误。
- 如果需要查找的信息比较笼统（例如概括案件），可以到 `description` 或 `content` 属性（如果有）中以部分关键词查找更多信息。关键词可以更精炼，以匹配更多的案例进行筛选。

## **反诈骗知识图谱数据模式**

### **节点类型 (Node Type)**

#### 1. **案件**
- **属性**：
  - `name`：案件的名称，字符串类型。
  - `type`：案件类型，分类标签，枚举类型，取值范围为：`刑事`、`民事`、`行政`、`执行`、`其他`。
  - `description`：案件的简单描述，文本类型。
  - `date_of_incident`：案发时间，Date 类型，如 `date("2020-01-01")`。（不可缺失）
  - `date_of_judgment`：审判时间，Date 类型，如 `date("2020-01-01")`。（可缺失）

#### 2. **人物**（尽量不要缺失）
- **属性**：
  - `name`：人物的全名，字符串类型。
  - `gender`：枚举类型，取值范围为：`男`、`女`、`未知`。（可缺失）
  - `birthday`：Date 类型。（可缺失）
  - `career`：人物的职业，字符串类型。（可缺失）
  - `education`：人物的学历或教育经历，字符串类型。（可缺失）
  - `description`：关于人物的详细描述，文本类型。

#### 3. **机构**（可缺失）
- **属性**：
  - `name`：机构的全称，字符串类型。
  - `type`：分类标签，字符串类型，可以是：`政府机构`、`企业`、`事业单位`、`社会团体`、 等（可缺失）
  - `description`：关于机构的详细描述，文本类型。

#### 4. **地点**（尽量不要缺失）
- **属性**：
  - `name`：地点的详细地址，字符串类型。
  - `province`：省/自治区/直辖市名称，不需要行政区划名，字符串类型（如“广东”，不要写成“广东省”）。
  - `city`：地级市名称，不需要行政区划名，字符串类型（如“广州”，不要写成“广州市”）。（可缺失）
  - `district`：区/县名称，不需要行政区划名，字符串类型（如“天河”，不要写成“天河区”）。（可缺失）

#### 5. **工具**（尽量不要缺失）
- **属性**：
  - `name`：工具的名称，字符串类型。
  - `type`：分类标签，枚举类型，取值范围为：`社交软件`、`银行卡`、`手机`、`短信`、`其他`。
  - `usage`：工具在诈骗中的用途，字符串类型（如“冒充好友”、“冒充公检法”）。

#### 6. **诈骗类型**（不能缺失！！）
- **属性**：
  - `name`：诈骗类型的名称，字符串类型。
  - `subtype`：诈骗的具体手法，字符串类型（如“冒充公检法”、“虚假投资”）。

#### 7. **实体资产**
- **属性**：
  - `name`：资产的名称，字符串类型。
  - `type`：分类标签，字符串类型，可以为：`房产`、`车辆`、`股票`、`钱财`、等
  - `amount`：资产的数量，数值类型。
  - `unit`：资产的计量单位，字符串类型（如“元”、“平方米”、“套”）。

#### 8. **罪名**（可缺失）
- **属性**：
  - `name`：罪名的全称，字符串类型。

#### 9. **法律法规**（可缺失）
- **属性**：
  - `name`：法律法规的名称，字符串类型。
  - `type`：分类标签，字符串类型，可以为：`刑法`、`民法`、`行政法`、`商法`、`其他`。
  - `description`：法律法规的具体条款或内容，文本类型。

---

### **关系类型 (Relationship Type)**

#### 1. **涉及被害人**
- **定义**：案件与被害人之间的关系。
- **方向**：`案件 -> 人物` 或 `案件 -> 机构`。
- **属性**：
  - 无。

#### 2. **涉及嫌疑人**
- **定义**：案件与嫌疑人或被告人之间的关系。
- **方向**：`案件 -> 人物` 或 `案件 -> 机构`。
- **属性**：
  - 无。

#### 3. **属于组织**（可缺失）
- **定义**：人物隶属于某个机构的关系。
- **方向**：`人物 -> 机构`。
- **属性**：
  - `career`：人物在机构中的职位，字符串类型。

#### 4. **所在地**（可缺失）
- **定义**：人物或机构所在的地理位置。
- **方向**：`人物 -> 地点` 或 `机构 -> 地点`。
- **属性**：
  - 无。

#### 5. **案发地点**（可缺失）
- **定义**：案件发生的位置。
- **方向**：`案件 -> 地点`。
- **属性**：
  - 无。

#### 8. **触犯法律法规**（可缺失）
- **定义**：人物或机构违反的法律法规。
- **方向**：`人物 -> 法律法规` 或 `机构 -> 法律法规`。
- **属性**：
  - 无。

#### 9. **诈骗类型**（不可缺失！！）
- **定义**：案件所属的诈骗类型。
- **方向**：`案件 -> 诈骗类型`。
- **属性**：
  - 无。

#### 11. **涉案工具**
- **定义**：案件中使用的工具。
- **方向**：`案件 -> 工具`。
- **属性**：
  - 无。

#### 12. **人物关系**（可缺失）
- **定义**：人物之间的关联。
- **方向**：`人物 -> 人物`。
- **属性**：
  - `type`：分类标签，字符串类型，可以为：`家人`、`朋友`、`同伙`、`其他` 等。（不可缺失）

#### 13. **涉案资产**（不可缺失！！）
- **定义**：案件中涉及的资产。
- **方向**：`案件 -> 实体资产`。
- **属性**：
  - 无。

#### 14. **罪名**（不可缺失！！）
- **定义**：人物或机构被指控的罪名。
- **方向**：`人物 -> 罪名` 或 `机构 -> 罪名`。
- **属性**：
  - 无。

#### 15. **刑事判决**（可缺失）
- **定义**：案件对人物或机构的判决结果。
- **方向**：`案件 -> 人物` 或 `案件 -> 机构`。
- **属性**：
  - `type`：分类标签，字符串类型，可以为：`缓刑`、`有期徒刑`、`无期徒刑`、`死刑`、`罚款`。（不可缺失）
  - `刑期`：刑罚的时长，duration 类型，如 `duration({{years:2, months:5}})`。（可缺失）
  - `罚金`：罚款金额，数值类型（单位为元）。（可缺失）

#### 16. **赔偿量**（可缺失）
- **定义**：人物或机构需要赔偿的资产。
- **方向**：`人物 -> 实体资产` 或 `机构 -> 实体资产`。
- **属性**：
  - 无。

#### 17. **赔偿给**（可缺失）
- **定义**：资产赔偿的对象。
- **方向**：`实体资产 -> 人物` 或 `实体资产 -> 机构`。
- **属性**：
  - 无。

Example Cypher Statements:

1. 数据库中有多少案例？
```cypher
MATCH (c:案件)
RETURN count(c) AS case_count
```

2. 使用手机诈骗的案例有哪些？
```cypher
MATCH (c:案件)-[r:涉案工具]->(t:工具)
WHERE t.name CONTAINS '手机' OR t.type = '手机'
RETURN c.name AS case_name, c.description AS case_description
LIMIT 8
```

3. 有哪些人涉及到了虚假投资？
```cypher
MATCH (c:案件)-[r:诈骗类型]->(t:诈骗类型)
WHERE t.name CONTAINS '投资' OR t.subtype CONTAINS '投资'
MATCH (c)-[r:涉案嫌疑人]->(p:人物)
RETURN p.name AS person_name, p.description AS person_description
LIMIT 8
```

4. 涉案金额最多的几个案例
```cypher
MATCH (c:案件)-[r:涉案资产]->(a:实体资产)
WHERE a.type = '钱财' AND a.unit = '元'
RETURN c.name AS caseName, SUM(a.amount) AS totalAmount
ORDER BY totalAmount DESC
LIMIT 8
```

5. 使用各类工具的诈骗案例分别占比多少？
```cypher
MATCH (case:案件)-[:涉案工具]->(tool:工具)
WITH tool.type AS tool_type, count(case) AS case_count
MATCH (all_case:案件)
WITH tool_type, case_count, count(all_case) AS total_cases
RETURN tool_type, toFloat(case_count) / toFloat(total_cases) * 100 AS percentage
ORDER BY percentage DESC
LIMIT 8

6. 涉嫌团伙作案的案件有哪些？
```cypher
MATCH (c:案件)-[r:涉案嫌疑人]->(p:人物)
WITH c, count(p) AS suspect_count
WHERE suspect_count > 1
RETURN c.name AS case_name, c.description AS case_description

7. 与嫖娼有关的案件有哪些？
```cypher
MATCH (c:案件)
WHERE c.description CONTAINS '嫖' OR c.content CONTAINS '娼'
RETURN c.name AS case_name, c.description AS case_description
```

Schema:
{schema}

Question:
{question}
"""

cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

_cypher_qa_chain = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    verbose=True,
    cypher_prompt=cypher_prompt,
    allow_dangerous_requests=True
)


def cypher_qa(question: str):
  """Run Cypher QA with graceful fallback so tool failures don't break the chat."""
  try:
    output = _cypher_qa_chain.invoke({"query": question})
    if isinstance(output, dict):
      return output.get("result") or str(output)
    return str(output)
  except Exception as e:
    return f"知识图谱查询暂时不可用：{e}"