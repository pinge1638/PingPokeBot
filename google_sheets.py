import os
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_sheet():
    private_key = os.getenv("GOOGLE_PRIVATE_KEY")

    credentials_info = {
        "type": "service_account",
        "client_email": os.getenv("GOOGLE_SERVICE_ACCOUNT_EMAIL"),
        "private_key": private_key.replace("\\n", "\n"),
    }

    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)

    sheet = client.open_by_key(
        os.getenv("GOOGLE_SHEET_ID")
    )

    return sheet.worksheet("Products")


def get_products():
    sheet = get_sheet()

    rows = sheet.get_all_records()

    products = []

    for row in rows:
        if str(row.get("Hidden", "NO")).upper() == "YES":
            continue

        products.append({
            "product_id": str(row["Product ID"]),
            "name": str(row["Name"]),
            "description": str(row["Description"]),
            "category": str(row["Category"]),
            "type": str(row["Type"]),
            "cost": float(row["Cost"]),
            "price": float(row["Price"]),
            "stock": int(row["Stock"]),
        })

    return products


if __name__ == "__main__":
    products = get_products()

    for product in products:
        print(product)
