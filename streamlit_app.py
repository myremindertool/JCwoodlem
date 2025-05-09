import streamlit as st
import os
import re
from datetime import datetime
import hashlib

def parse_chat(content):
    android_pattern = re.compile(r"(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}) - (.*?): (.*)")
    iphone_pattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}:\d{2} [APMapm]{2})\] (.*?): (.*)")
    messages = []
    for match in android_pattern.findall(content):
        try:
            dt = datetime.strptime(f"{match[0]} {match[1]}", "%d/%m/%Y %H:%M")
            messages.append({"datetime": dt, "sender": match[2], "message": match[3]})
        except: continue
    for match in iphone_pattern.findall(content):
        try:
            dt = datetime.strptime(f"{match[0]} {match[1]}", "%d/%m/%Y %I:%M:%S %p")
            messages.append({"datetime": dt, "sender": match[2], "message": match[3]})
        except: continue
    return sorted(messages, key=lambda x: x["datetime"])

def sender_color(sender):
    colors = ["#f0f8ff", "#e6ffe6", "#fff0f5", "#fffdd0", "#e0ffff", "#f5f5dc"]
    idx = int(hashlib.sha256(sender.encode()).hexdigest(), 16) % len(colors)
    return colors[idx]

def get_initials(name):
    parts = name.strip().split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][0].upper()

# Page config
st.set_page_config(page_title="JC WhatsApp Chat Viewer", layout="wide")
st.markdown("""
    <style>
        .message-box {
            border-radius: 10px;
            padding: 0.75rem;
            margin: 0.25rem 0;
            display: flex;
            flex-direction: row;
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
        .avatar {
            width: 2.2rem;
            height: 2.2rem;
            border-radius: 50%;
            background: #ccc;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 0.75rem;
        }
        .chat-scroll-wrapper {
            height: 600px;
            overflow-y: scroll;
            padding-right: 1rem;
            margin-top: 0;
            border-top: 1px solid #eee;
            scrollbar-gutter: stable;
        }
        section.main > div { padding-top: 0rem !important; }
        .block-container { padding-top: 0rem !important; }
        a { text-decoration: none; font-weight: bold; font-size: 0.9rem; }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("💬 JC WhatsApp Multi-Chat Viewer")
st.markdown("_Created by **JC**_")
st.markdown("---")

chat_files = [f for f in os.listdir() if f.endswith(".txt") and f.lower() != "requirements.txt"]
selected_files = st.multiselect("📁 Select chat file(s) to view:", chat_files)

if selected_files:
    cols = st.columns(len(selected_files))
    for idx, file in enumerate(selected_files):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read().replace('\u202f', ' ').replace('\u200e', '')
        messages = parse_chat(content)
        if not messages:
            cols[idx].warning(f"{file} is empty or invalid.")
            continue
        senders = sorted(set(m['sender'] for m in messages))
        with cols[idx]:
            st.subheader(file)
            selected_senders = st.multiselect(f"👤 Senders ({file})", senders, default=senders, key=f"senders_{idx}")
            search_term = st.text_input(f"🔍 Search ({file})", "", key=f"search_{idx}")

            # Filtered messages
            filtered_messages = [
                m for m in messages
                if m["sender"] in selected_senders and search_term.lower() in m["message"].lower()
            ]

            st.info(f"Parsed {len(messages)} messages. Showing {len(filtered_messages)} after filters.")

            # Scroll buttons
            st.markdown("""
                <div style='display:flex; gap: 10px; margin-bottom: 10px;'>
                    <a href='#top-anchor' onclick="document.getElementById('top-anchor').scrollIntoView({behavior:'smooth'});">🔝 Top</a>
                    <a href='#middle-anchor' onclick="document.getElementById('middle-anchor').scrollIntoView({behavior:'smooth'});">🔽 Middle</a>
                    <a href='#bottom-anchor' onclick="document.getElementById('bottom-anchor').scrollIntoView({behavior:'smooth'});">🔚 Bottom</a>
                </div>
                <div id='top-anchor'></div>
            """, unsafe_allow_html=True)

            # Start scroll container
            st.markdown("<div class='chat-scroll-wrapper'>", unsafe_allow_html=True)

            if not filtered_messages:
                st.markdown("<p style='color:gray'>No messages match your filters or search.</p>", unsafe_allow_html=True)
            else:
                last_date = ""
                for i, m in enumerate(filtered_messages):
                    current_date = m['datetime'].strftime('%d %b %Y')
                    if current_date != last_date:
                        st.markdown(f"### 📅 {current_date}")
                        last_date = current_date

                    # Drop middle anchor at halfway point
                    if i == len(filtered_messages) // 2:
                        st.markdown("<div id='middle-anchor'></div>", unsafe_allow_html=True)

                    initials = get_initials(m['sender'])
                    avatar = f"<div class='avatar'>{initials}</div>"
                    color = sender_color(m['sender'])
                    sender_line = f"<span class='sender-header'>{m['sender']}<span class='timestamp'> &nbsp;&nbsp;{m['datetime'].strftime('%I:%M %p')}</span></span>"
                    st.markdown(f"""
                        <div class='message-box' style='background-color: {color};'>
                            {avatar}
                            <div>
                                {sender_line}
                                <div>{m['message']}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                # Bottom anchor
                st.markdown("<div id='bottom-anchor'></div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
