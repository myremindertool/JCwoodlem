import streamlit as st
import os
import re
from datetime import datetime

# Function to parse chat from txt
def parse_chat(content):
    android_pattern = re.compile(r"(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}) - (.*?): (.*)")
    iphone_pattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}:\d{2} [APMapm]{2})\] (.*?): (.*)")
    
    messages = []

    for match in android_pattern.findall(content):
        try:
            dt = datetime.strptime(f"{match[0]} {match[1]}", "%d/%m/%Y %H:%M")
            messages.append({"datetime": dt, "sender": match[2], "message": match[3]})
        except:
            continue

    for match in iphone_pattern.findall(content):
        try:
            dt = datetime.strptime(f"{match[0]} {match[1]}", "%d/%m/%Y %I:%M:%S %p")
            messages.append({"datetime": dt, "sender": match[2], "message": match[3]})
        except:
            continue

    return sorted(messages, key=lambda x: x["datetime"])

# Streamlit UI
st.set_page_config(page_title="JC WhatsApp Chat Viewer", layout="wide")
st.title("💬 JC WhatsApp Multi-Chat Viewer")
st.markdown("_Created by **JC**_")
st.markdown("---")

# Only show .txt files (exclude requirements.txt)
available_files = [f for f in os.listdir() if f.endswith(".txt") and f.lower() != "requirements.txt"]
selected_file = st.selectbox("📂 Choose a chat file to view:", available_files)

if selected_file:
    with open(selected_file, "r", encoding="utf-8") as file:
        content = file.read()

    content = content.replace('\u202f', ' ').replace('\u200e', '')
    messages = parse_chat(content)

    if not messages:
        st.warning("No messages found. Please ensure it's in WhatsApp export format.")
    else:
        senders = sorted(set(m['sender'] for m in messages))
        selected_senders = st.multiselect("👤 Filter by sender(s):", options=senders, default=senders)

        filtered = [m for m in messages if m['sender'] in selected_senders]

        with st.container():
            for m in filtered:
                is_me = m['sender'].lower() in ['you', 'me', '🔄']
                with st.chat_message("user" if is_me else "assistant"):
                    st.markdown(f"**{m['sender']}**  ")
                    st.caption(m['datetime'].strftime("%d %b %Y • %I:%M %p"))
                    st.markdown(m['message'])

        st.success(f"✅ Showing {len(filtered)} messages from '{selected_file}'")
