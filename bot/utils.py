import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
import re


def _sanitize_markdown(text: str) -> str:
    """Normalize common LLM formatting artifacts so Markdown tables render correctly."""
    if not isinstance(text, str):
        return str(text)

    # Remove duplicated Chinese punctuation often produced by streamed joins.
    text = text.replace("： ：", "：").replace("。 。", "。")
    # Split glued table rows that were emitted on the same line.
    text = re.sub(r"\|\s+\|", "\n", text)

    fixed_lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # Drop empty pseudo-table lines like "| |" / "||".
        if re.fullmatch(r"\|\s*\|+\s*", line):
            continue

        # Rebuild rows that contain multiple columns but inconsistent spacing.
        if line.count("|") >= 2:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            cells = [cell for cell in cells if cell]
            if len(cells) >= 2:
                line = "| " + " | ".join(cells) + " |"

        fixed_lines.append(line)

    return "\n".join(fixed_lines).strip()

# tag::write_message[]
def write_message(role, content, save = True):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """
    # Append to session state


    # Write to UI
    with st.chat_message(role):
        if type(content) == str:
            result = content
        else:
            with st.spinner("正在生成内容……"):
                with st.expander("思考链", expanded=False):
                    try:
                        stream_result = st.write_stream(content)
                    except Exception as e:
                        stream_result = f"抱歉，生成回答时出现异常：{e}"

                    if isinstance(stream_result, str):
                        result = stream_result
                    elif isinstance(stream_result, list) and stream_result:
                        last_item = stream_result[-1]
                        if isinstance(last_item, dict) and "output" in last_item:
                            result = last_item["output"]
                        else:
                            result = "\n".join(str(item) for item in stream_result)
                    else:
                        result = str(stream_result)
        result = _sanitize_markdown(result)
        st.markdown(result)
        if save:
            st.session_state.messages.append({"role": role, "content": result})
# end::write_message[]

# tag::get_session_id[]
def get_session_id():
    return get_script_run_ctx().session_id
# end::get_session_id[]