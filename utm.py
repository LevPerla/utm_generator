import streamlit as st
import pandas as pd
import os
import re

# Хранилище utm-ссылок
# Путь к CSV
CSV_PATH = "utm_history.csv"

# Хранилище utm-ссылок
if 'utm_links' not in st.session_state:
    if os.path.exists(CSV_PATH):
        st.session_state.utm_links = pd.read_csv(CSV_PATH).to_dict(orient="records")
    else:
        st.session_state.utm_links = []
        

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
            pd.DataFrame(st.session_state.utm_links).to_csv(CSV_PATH, index=False)

# Таблица результатов
if st.session_state.utm_links:
    df = pd.DataFrame(st.session_state.utm_links)
    st.subheader("История UTM меток")
    st.dataframe(df)