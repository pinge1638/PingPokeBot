import os
import gspread
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_spreadsheet():

    private_key = os.getenv("GOOGLE_PRIVATE_KEY")

    credentials_info = {
        "type": "service_account",
        "client_email": os.getenv("GOOGLE_SERVICE_ACCOUNT_EMAIL"),
        "private_key": private_key.replace("\\n", "\n"),
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)

    return client.open_by_key(
        os.getenv("GOOGLE_SHEET_ID")
    )


def get_sheet():

    spreadsheet = get_spreadsheet()

    return spreadsheet.worksheet("Products")


def get_products():

    spreadsheet = get_spreadsheet()

    products = []

    # =========================
    # READY STOCK
    # =========================

    ready_sheet = spreadsheet.worksheet("Products")
    ready_rows = ready_sheet.get_all_records()

    for row in ready_rows:

        if str(row.get("Hidden", "NO")).upper() == "YES":
            continue

        products.append({
            "product_id": str(row["Product ID"]),
            "name": str(row["Name"]),
            "description": str(row["Description"]),
            "category": str(row["Category"]),
            "type": "Ready Stock",
            "cost": float(
                str(row["Cost"])
                .replace("$", "")
                .replace(",", "")
                .strip()
            ),
            "price": float(
                str(row["Price"])
                .replace("$", "")
                .replace(",", "")
                .strip()
            ),
            "stock": int(row["Stock"]),
        })

    # =========================
    # PREORDERS
    # =========================

    preorder_sheet = spreadsheet.worksheet("Preorders")
    preorder_rows = preorder_sheet.get_all_records()

    for row in preorder_rows:

        if str(row.get("Hidden", "NO")).upper() == "YES":
            continue

        products.append({
            "product_id": str(row["Product ID"]),
            "name": str(row["Name"]),
            "description": str(row["Description"]),
            "category": str(row["Category"]),
            "type": "Preorder",
            "cost": float(
                str(row["Cost"])
                .replace("$", "")
                .replace(",", "")
                .strip()
            ),
            "price": float(
                str(row["Price"])
                .replace("$", "")
                .replace(",", "")
                .strip()
            ),
            "stock": int(row["Stock"]),
        })

    return products


def update_stock(product_id, change):

    sheet = get_sheet()

    rows = sheet.get_all_records()

    for row_number, row in enumerate(rows, start=2):

        if str(row["Product ID"]) == str(product_id):

            current_stock = int(row["Stock"])
            new_stock = current_stock + change

            if new_stock < 0:
                return False

            sheet.update_cell(
                row_number,
                8,
                new_stock,
            )

            return True

    return False


if __name__ == "__main__":

    products = get_products()

    for product in products:
        print(product)
