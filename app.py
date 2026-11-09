import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# page configuration
st.set_page_config(
    page_title="cisa tabletop exercise platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# resolve data path across different run locations and environments
def find_data_dir():
    candidates = [
        Path(__file__).resolve().parent / "data" / "processed",
        Path(__file__).resolve().parent.parent / "data" / "processed",
        Path.cwd() / "data" / "processed",
        Path.cwd().parent / "data" / "processed",
    ]
    for c in candidates:
        if (c / "cisa_classified_events.csv").exists() and (c / "cisa_discussion_questions.csv").exists():
            return c
    return candidates[0]

data_path = find_data_dir()
events_file = data_path / "cisa_classified_events.csv"
questions_file = data_path / "cisa_discussion_questions.csv"

@st.cache_data
def load_datasets():
    events_df = pd.read_csv(events_file)
    questions_df = pd.read_csv(questions_file)
    return events_df, questions_df

try:
    df_events, df_questions = load_datasets()
except Exception as e:
    st.error(f"error loading data files from {data_path}: {e}")
    st.info("please ensure cisa_classified_events.csv and cisa_discussion_questions.csv exist in data/processed/")
    st.stop()

# initialize session state for navigation and answers
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "selected_manual" not in st.session_state:
    st.session_state.selected_manual = df_events["manual_title"].iloc[0]

# sidebar: exercise setup
st.sidebar.title("🛡️ exercise control")
available_manuals = df_events["manual_title"].unique().tolist()

chosen_manual = st.sidebar.selectbox(
    "select scenario package:",
    available_manuals,
    index=available_manuals.index(st.session_state.selected_manual)
)

# reset step index if scenario is switched
if chosen_manual != st.session_state.selected_manual:
    st.session_state.selected_manual = chosen_manual
    st.session_state.current_index = 0
    st.rerun()

scenario_events = df_events[df_events["manual_title"] == chosen_manual].reset_index(drop=True)
total_injects = len(scenario_events)
idx = st.session_state.current_index
current_event = scenario_events.iloc[idx]

# sidebar: progress & timeline jump
st.sidebar.markdown("---")
st.sidebar.subheader("scenario timeline")
for i, row in scenario_events.iterrows():
    day_label = row["day"] if pd.notna(row["day"]) else row["section"]
    btn_label = f"{'▶ ' if i == idx else ''}inject {i+1}: {day_label}"
    if st.sidebar.button(btn_label, key=f"nav_{i}", use_container_width=True):
        st.session_state.current_index = i
        st.rerun()

# main interface: exercise header
st.title(f"{chosen_manual} tabletop simulation")
timeline_str = current_event["day"] if pd.notna(current_event["day"]) else current_event["section"]
st.caption(f"exercise module: {current_event['section']} | timeline: {timeline_str}")

# progress bar
progress_val = (idx + 1) / total_injects
st.progress(progress_val, text=f"inject {idx + 1} of {total_injects}")

# inject card
st.markdown("### 🚨 situational inject")
col_narrative, col_intel = st.columns([2.2, 1])

with col_narrative:
    st.info(f"**inject id:** `{current_event['inject_id']}`\n\n{current_event['event_description']}")

with col_intel:
    st.metric(label="classified threat type", value=str(current_event["threat_type"]))
    st.warning(f"**operational impact:**\n\n{current_event['business_impact']}")

st.markdown("---")

# match questions to the current event context
if pd.notna(current_event["day"]):
    matching_questions = df_questions[
        (df_questions["manual_title"] == chosen_manual) &
        (df_questions["day"] == current_event["day"])
    ]
else:
    matching_questions = df_questions[
        (df_questions["manual_title"] == chosen_manual) &
        (df_questions["section"] == current_event["section"])
    ]

# fallback if manual questions are grouped at module level
if matching_questions.empty:
    matching_questions = df_questions[
        (df_questions["manual_title"] == chosen_manual) &
        (df_questions["section"] == current_event["section"])
    ]

st.markdown("### 📋 strategic decision prompts")

if not matching_questions.empty:
    for _, q in matching_questions.iterrows():
        q_id = q["question_id"]
        q_text = q["question_text"]
        
        st.markdown(f"**[{q_id}]** {q_text}")
        default_val = st.session_state.user_answers.get(q_id, "")
        
        user_input = st.text_area(
            label=f"enter organizational decision / notes for {q_id}:",
            value=default_val,
            key=f"input_{q_id}",
            height=100
        )
        st.session_state.user_answers[q_id] = user_input
else:
    st.write("no specific discussion prompts attached to this step. review operational impacts and prepare for subsequent injects.")

# navigation controls
st.markdown("---")
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 3])

with btn_col1:
    if st.button("⬅️ previous inject", disabled=(idx == 0), use_container_width=True):
        st.session_state.current_index -= 1
        st.rerun()

with btn_col2:
    if st.button("next inject ➡️", disabled=(idx == total_injects - 1), use_container_width=True):
        st.session_state.current_index += 1
        st.rerun()

# after-action report (aar) generator
st.sidebar.markdown("---")
st.sidebar.subheader("export deliverables")

if st.sidebar.button("generate after-action report", use_container_width=True):
    report_lines = [
        f"# cisa cybersecurity tabletop exercise: after-action report",
        f"**scenario package:** {chosen_manual}",
        f"**generated on:** {datetime.now().strftime('%y-%m-%d %h:%m:%s')}",
        "\n## recorded decisions & discussion notes\n"
    ]
    
    for q_id, response in st.session_state.user_answers.items():
        if response.strip():
            matched = df_questions[df_questions["question_id"] == q_id]
            q_prompt = matched["question_text"].iloc[0] if not matched.empty else ""
            report_lines.append(f"### {q_id}")
            report_lines.append(f"**prompt:** {q_prompt}")
            report_lines.append(f"**response:**\n{response}\n")
    
    aar_markdown = "\n".join(report_lines)
    
    st.sidebar.download_button(
        label="⬇️ download report (.md)",
        data=aar_markdown,
        file_name=f"cisa_tabletop_aar_{chosen_manual.lower().replace(' ', '_')}.md",
        mime="text/markdown",
        use_container_width=True
    )
