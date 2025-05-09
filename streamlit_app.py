import streamlit as st
import os
import re
from datetime import datetime
import hashlib

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

# Generate consistent color based on sender name
def sender_color(sender):
    colors = ["#f0f8ff", "#e6ffe6", "#fff0f5", "#fffdd0", "#e0ffff", "#f5f5dc"]
    idx = int(hashlib.sha256(sender.encode()).hexdigest(), 16) % len(colors)
    return colors[idx]

# Streamlit UI
st.set_page_config(page_title="JC WhatsApp Chat Viewer", layout="wide")
st.markdown("""
    <style>
        .message-box {
            border-radius: 10px;
            padding: 0.75rem;
            margin: 0.25rem 0;
            display: flex;
            flex-direction: column;
            font-size: 0.95rem;
            border-left: 5px solid #ccc;
        }
        .sender-header {
            font-weight: 600;
            color: #333;
            margin-bottom: 0.25rem;
        }
        .timestamp {
            font-size: 0.75rem;
            color: #888;
            margin-left: 0.5rem;
        }
        .chat-scroll-wrapper {
            height: 600px;
            overflow-y: scroll;
            padding-right: 1rem;
            margin-top: 1rem;
            border-top: 1px solid #eee;
        }
        .stMultiSelect > div[data-baseweb="select"] {
            margin-bottom: 0 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("💬 JC WhatsApp Multi-Chat Viewer")
st.markdown("_Created by **JC**_")
st.markdown("---")

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

        st.markdown("""
            <div class='chat-scroll-wrapper'>
        """, unsafe_allow_html=True)

        for m in [msg for msg in messages if msg['sender'] in selected_senders]:
            color = sender_color(m['sender'])
            icon = "💬"
            sender_line = f"<span class='sender-header'>{icon} {m['sender']}<span class='timestamp'> &nbsp;&nbsp;&nbsp;{m['datetime'].strftime('%d %b %Y • %I:%M %p')}</span></span>"
            st.markdown(f"""
                <div class='message-box' style='background-color: {color};'>
                    {sender_line}
                    <div>{m['message']}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.success(f"✅ Showing {len([m for m in messages if m['sender'] in selected_senders])} messages from '{selected_file}'")
