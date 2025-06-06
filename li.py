
import streamlit as st
import string
import secrets
import pyperclip
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_lottie import st_lottie

# Custom CSS for a lively bright theme
st.markdown(
    """
    <style>
        body {
            background-color: #FF69B4; /* Bright pink */
            color: #333333;
        }
        .stApp {
            background: linear-gradient(to bottom, #FFB6C1, #FF69B4);
            border-radius: 10px;
            padding: 20px;
        }
        .stCheckbox label {
            transition: transform 0.3s ease-in-out;
        }
        .stCheckbox input:checked + label {
            transform: scale(1.2);
            color: #FF4500;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Load animation
def load_lottiefile(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_coding = load_lottiefile("C:/Users/micro/sky/lottiefiles/Animation - 1742018924155 (2).json")
st_lottie(lottie_coding, key="hello")

# Google Sheets Authentication
def connect_to_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("pawd.json", scope)
    client = gspread.authorize(creds)
    return client

# Function to update password in Google Sheets
def update_gsheet(application, password):
    try:
        client = connect_to_gsheet()
        sheet = client.open("PasswordStorage").sheet1
        data = sheet.get_all_records()
        app_names = [row["Application"] for row in data]

        if application in app_names:
            row_index = app_names.index(application) + 2  # Adjust for header row
            sheet.update_cell(row_index, 2, password)
        else:
            sheet.append_row([application, password])

        st.success(f"Password updated for {application} in Google Sheets.")
    except Exception as e:
        st.error(f"Error updating Google Sheets: {e}")

# Generate Auto-Generated Password
def generate_password(length=12, include_numbers=True, include_special_chars=True, include_uppercase=True, easy_to_read=False):
    PET_NAMES = ["Lucky", "Bella", "Charlie", "Max", "Daisy", "Milo", "Bailey", "Coco", "Rocky", "Luna"]
    SPECIAL_SYMBOLS = "@#$%&*_"

    if easy_to_read:
        pet_name = secrets.choice(PET_NAMES)
        special_char = secrets.choice(SPECIAL_SYMBOLS)
        number = ''.join(secrets.choice(string.digits) for _ in range(secrets.randbelow(3) + 3))  # Generates 3-5 digit numbers
        return f"{pet_name}{special_char}{number}"

    characters = string.ascii_lowercase
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_numbers:
        characters += string.digits
    if include_special_chars:
        characters += SPECIAL_SYMBOLS

    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

# Custom Password Validation
def validate_custom_password(password, include_numbers, include_special_chars):
    special_symbols = "@#$%&*_"
    if include_numbers and not password.isdigit():
        return "Only numbers are allowed when 'Include Numbers' is selected."
    if include_special_chars and any(c not in special_symbols for c in password):
        return "Only special characters (@, #, $, %, _, *) are allowed when 'Include Special Characters' is selected."
    if include_special_chars is False and any(c in special_symbols for c in password):
        return "Symbols are not allowed unless 'Include Special Characters' is selected."
    return None

# Process Custom Password
def process_custom_password(password, include_numbers, remove_spaces, include_uppercase, include_special_chars):
    error_msg = validate_custom_password(password, include_numbers, include_special_chars)
    if error_msg:
        st.error(error_msg)
        return ""
    if remove_spaces:
        password = password.replace(" ", "")
    if include_uppercase:
        password = password.capitalize()
    return password

# Copy Password to Clipboard
def copy_to_clipboard(password, application):
    pyperclip.copy(password)
    st.success("Password copied to clipboard!")
    update_gsheet(application, password)

def main():
    st.title("🔮 Password Generator")
    application = st.text_input("Enter Application Name")

    if application:
        password_type = st.radio("Choose Password Type", ["Auto-Generated", "Custom Password"])

        if password_type == "Auto-Generated":
            include_numbers = st.checkbox("Include Numbers", value=True)
            include_special_chars = st.checkbox("Include Special Characters", value=True)
            include_uppercase = st.checkbox("Include Uppercase Letters", value=True)
            easy_to_read = st.checkbox("Easy-to-Read Password")

            password = generate_password(12, include_numbers, include_special_chars, include_uppercase, easy_to_read)
            st.session_state["password"] = password

        elif password_type == "Custom Password":
            include_numbers = st.checkbox("Include Numbers")
            remove_spaces = st.checkbox("Remove Spaces")
            include_uppercase = st.checkbox("Include First Letter Uppercase")
            include_special_chars = st.checkbox("Include Special Characters")

            custom_password = st.text_input("Enter Custom Password", type="password")
            if custom_password:
                processed_password = process_custom_password(custom_password, include_numbers, remove_spaces, include_uppercase, include_special_chars)
                if processed_password:
                    st.session_state["password"] = processed_password
                    st.success("Custom password set successfully!")
        
        if "password" in st.session_state:
            password = st.session_state["password"]
            st.text_input("Generated Password", value=password, type="password")
            if st.button("Copy Password"):
                copy_to_clipboard(password, application)

if __name__ == "__main__":
    main()