import streamlit as st
import pandas as pd
import os
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import io

# Инициализация Google Sheets
SPREADSHEET_ID = "1eQiCqwXu49xEa3leUc8fgkN05hom_K0sbwK9868V4Zc"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_worksheet():
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)
    return sheet.sheet1

def load_utm_links():
    ws = get_worksheet()
    return ws.get_all_records()

def save_utm_links(data):
    ws = get_worksheet()
    ws.clear()
    ws.append_row(["utm_source", "utm_medium", "utm_campaign", "utm_url"])
    for row in data:
        ws.append_row([row["utm_source"], row["utm_medium"], row["utm_campaign"], row["utm_url"]])

if 'utm_links' not in st.session_state:
    st.session_state.utm_links = load_utm_links()
        
st.title("UTM Генератор и Валидатор")

# Валидация одного поля
def validate_utm_field(field_name, value):
    if not value:
        return f"{field_name} не может быть пустым"
    if not re.match(r"^[a-zA-Z0-9_\-]+$", value):
        return f"{field_name} содержит недопустимые символы (разрешены: буквы, цифры, '-', '_')"
    return None

# Форма ввода
with st.form("utm_form"):
    utm_source = st.text_input("utm_source")
    utm_medium = st.text_input("utm_medium")
    utm_campaign = st.text_input("utm_campaign")
    submit = st.form_submit_button("Сгенерировать")

    if submit:
        errors = []
        for name, value in {
            "utm_source": utm_source,
            "utm_medium": utm_medium,
            "utm_campaign": utm_campaign
        }.items():
            err = validate_utm_field(name, value)
            if err:
                errors.append(err)

        if errors:
            for e in errors:
                st.error(e)
        else:
            # Проверка на дублирование
            is_duplicate = any(
                row["utm_source"] == utm_source and
                row["utm_medium"] == utm_medium and
                row["utm_campaign"] == utm_campaign
                for row in st.session_state.utm_links
            )
            if is_duplicate:
                st.warning("Такая UTM комбинация уже существует в таблице.")
                st.stop()

            utm_url = f"?utm_source={utm_source}&utm_medium={utm_medium}&utm_campaign={utm_campaign}"
            st.success("UTM успешно сгенерирован!")
            st.code(utm_url)
            st.session_state.utm_links.append({
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_campaign": utm_campaign,
                "utm_url": utm_url
            })
            save_utm_links(st.session_state.utm_links)

# Таблица результатов
if st.session_state.utm_links:
    df = pd.DataFrame(st.session_state.utm_links)
    st.subheader("История UTM меток")
    st.dataframe(df)