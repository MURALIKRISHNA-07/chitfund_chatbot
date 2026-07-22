import time
import streamlit as st
from agents.conversation_agent import route
from database.conversations import save_conversation
from database.leads import save_lead

st.set_page_config(page_title="Chit Fund Adviser", page_icon="💰")
st.title("💰 Chit Fund Adviser")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{id(st.session_state)}"

if "breakdown_df" not in st.session_state:
    st.session_state.breakdown_df = None

if "breakdown_summary" not in st.session_state:
    st.session_state.breakdown_summary = None

if "show_lead_form" not in st.session_state:
    st.session_state.show_lead_form = False

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"])

if st.session_state.breakdown_df is not None:
    with st.chat_message("assistant"):
        if st.session_state.breakdown_summary:
            st.markdown("**Investment Summary**")
            cols = st.columns(3)
            for i, (key, val) in enumerate(st.session_state.breakdown_summary.items()):
                cols[i].metric(key, f"₹{val:,.2f}")
        st.dataframe(st.session_state.breakdown_df, use_container_width=True)
    st.session_state.breakdown_df = None
    st.session_state.breakdown_summary = None

if st.session_state.messages:
    if st.button("Interested? Share your details", key="lead_btn"):
        st.session_state.show_lead_form = True

if not st.session_state.messages:
    st.markdown("---")
    st.markdown("### 💡 Try asking")
    suggestions = [
        "How does a chit fund work?",
        "I want to invest ₹10,000 per month. Suggest a scheme",
        "Calculate dividend for ₹2,00,000 chit",
    ]
    cols = st.columns(3)
    for i, q in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(q, key=f"sugg_{i}"):
                st.session_state.messages.append({"role": "user", "text": q})
                with st.chat_message("user"):
                    st.markdown(q)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        start_time = time.time()
                        response = route(q, st.session_state.messages)
                        elapsed = time.time() - start_time
                    st.markdown(response)
                    st.caption(f"⚡ {elapsed:.1f}s")
                st.session_state.messages.append({"role": "assistant", "text": response})
                if st.session_state.breakdown_df is not None:
                    with st.chat_message("assistant"):
                        if st.session_state.breakdown_summary:
                            st.markdown("**Investment Summary**")
                            cols2 = st.columns(3)
                            for j, (key, val) in enumerate(st.session_state.breakdown_summary.items()):
                                cols2[j].metric(key, f"₹{val:,.2f}")
                        st.dataframe(st.session_state.breakdown_df, use_container_width=True)
                    st.session_state.breakdown_df = None
                    st.session_state.breakdown_summary = None
                save_conversation(st.session_state.user_id, st.session_state.messages)
                st.rerun()
    st.markdown("---")

if st.session_state.show_lead_form:
    with st.form("lead_form"):
        st.markdown("**Share your details and our team will contact you**")
        name = st.text_input("Your Name")
        mobile = st.text_input("Mobile Number")
        city = st.text_input("City")
        budget = st.number_input("Monthly Budget (₹)", min_value=0, step=1000)
        scheme = st.text_input("Interested Scheme (optional)")
        submitted = st.form_submit_button("Submit")

        if submitted and name and mobile:
            lead_id = save_lead({
                "name": name,
                "mobile": mobile,
                "city": city,
                "budget": budget,
                "interested_scheme": scheme,
            })
            st.success(f"Thank you {name}! Our team will contact you soon.")
            st.session_state.show_lead_form = False
            st.rerun()
        elif submitted:
            st.error("Please enter at least your name and mobile number.")

if prompt := st.chat_input("Ask about chit funds..."):
    st.session_state.messages.append({"role": "user", "text": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            start_time = time.time()
            response = route(prompt, st.session_state.messages)
            elapsed = time.time() - start_time

        st.markdown(response)
        st.caption(f"⚡ {elapsed:.1f}s")

    st.session_state.messages.append({"role": "assistant", "text": response})

    if st.session_state.breakdown_df is not None:
        with st.chat_message("assistant"):
            if st.session_state.breakdown_summary:
                st.markdown("**Investment Summary**")
                cols = st.columns(3)
                for i, (key, val) in enumerate(st.session_state.breakdown_summary.items()):
                    cols[i].metric(key, f"₹{val:,.2f}")
            st.dataframe(st.session_state.breakdown_df, use_container_width=True)
        st.session_state.breakdown_df = None
        st.session_state.breakdown_summary = None

    save_conversation(st.session_state.user_id, st.session_state.messages)
