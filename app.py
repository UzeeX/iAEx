import streamlit as st
import pandas as pd
import time
from playwright.sync_api import sync_playwright

URL = "https://iagestionprivee.ca/trouver-un-conseiller-iagestionprivee#by-location"

st.set_page_config(page_title="IA Gestion Privée – QC Advisors", layout="centered")

st.title("📊 IA Gestion Privée – Québec Advisors Extractor")
st.write("Extract all Québec-based advisors and export them as a CSV.")

@st.cache_data(show_spinner=False)
def scrape_qc_advisors():
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        page.wait_for_selector(".advisor-card", timeout=60000)

        # Scroll to load all advisors
        for _ in range(12):
            page.mouse.wheel(0, 4000)
            time.sleep(1)

        advisors = page.query_selector_all(".advisor-card")

        for advisor in advisors:
            def safe_text(selector):
                el = advisor.query_selector(selector)
                return el.inner_text().strip() if el else ""

            name = safe_text(".advisor-name")
            phone = safe_text(".advisor-phone")
            address = safe_text(".advisor-address")

            email_el = advisor.query_selector("a[href^='mailto:']")
            email = email_el.get_attribute("href").replace("mailto:", "") if email_el else ""

            # Keep Québec only
            if "QC" in address or "Québec" in address:
                rows.append({
                    "Name": name,
                    "Phone": phone,
                    "Email": email,
                    "Address": address,
                    "Province": "QC"
                })

        browser.close()

    return pd.DataFrame(rows)

if st.button("🚀 Run Québec Advisor Extraction"):
    with st.spinner("Scraping advisors… please wait"):
        df = scrape_qc_advisors()

    if df.empty:
        st.warning("No Québec advisors found.")
    else:
        st.success(f"Found {len(df)} Québec advisors")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            csv,
            "ia_gestion_privee_quebec_advisors.csv",
            "text/csv"
        )
