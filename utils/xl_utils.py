import openpyxl
import asyncio
from datetime import datetime
from config import settings


EXCEL_FILE_PATH = settings.EXCEL_FILE_PATH


async def write_order_to_excel(order_data):
    await asyncio.to_thread(_write_order_to_excel, order_data)


def _write_order_to_excel(order_data):
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE_PATH)
    except FileNotFoundError:
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.title = "Orders"
        sheet.append(
            [
                "Order ID",
                "User ID",
                "Product ID",
                "Product Name",
                "Quantity",
                "Price",
                "Address",
                "Payment Status",
                "Timestamp",
            ]
        )

    sheet = wb.active
    sheet.append(order_data)
    wb.save(EXCEL_FILE_PATH)


def generate_order_data(user_id, product_id, product_name, quantity, price, address):
    order_id = f"{user_id}_{product_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return [
        order_id,
        user_id,
        product_id,
        product_name,
        quantity,
        price,
        address,
        "Paid",
        timestamp,
    ]
