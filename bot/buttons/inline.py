from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from telebot import TeleBot, types
from datetime import datetime, timedelta

from bot.models import Product, Material

urlkb = InlineKeyboardMarkup(row_width=1)
urlbutton = InlineKeyboardButton(
    text='👨‍💻 Admin', url='https://t.me/Jamshid_Abdurahmonov1')
urlkb.add(urlbutton)


def create_confirmation_keyboard(report_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Tasdiqlash ✅", callback_data=f"confirm_{report_id}"), InlineKeyboardButton(text="Bekor qilish ❌", callback_data=f"cancel_{report_id}"))
    return markup
    
def create_days_keyboard(year=None, month=None):
    # If no year or month is provided, use the current month and year
    if year is None or month is None:
        today = datetime.now()
        year = today.year
        month = today.month

    # Create a new inline keyboard markup
    markup = types.InlineKeyboardMarkup(row_width=7)

    # Display the month and year as the title
    month_name = datetime(year, month, 1).strftime('%B %Y')
    title = types.InlineKeyboardButton(f"--- {month_name} ---", callback_data="ignore")
    markup.add(title)

    # Create buttons for each day of the month
    first_day = datetime(year, month, 1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    buttons = [types.InlineKeyboardButton(
        text=str(day),
        callback_data=f"date_{day:02d}.{month:02d}.{year}"
    ) for day in range(1, last_day.day + 1)]

    # Add buttons to the keyboard
    markup.add(*buttons)

    # Navigation buttons
    prev_month = (first_day - timedelta(days=1)).replace(day=1)
    next_month = (last_day + timedelta(days=1)).replace(day=1)
    navigation = [
        types.InlineKeyboardButton("<", callback_data=f"nav_{prev_month.year}_{prev_month.month}"),
        types.InlineKeyboardButton("x", callback_data="ignore"),
        types.InlineKeyboardButton(">", callback_data=f"nav_{next_month.year}_{next_month.month}")
    ]
    markup.add(*navigation)
    

    return markup


def create_day_night_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    
    # Add "Day" and "Night" buttons with respective callback data
    day_button = InlineKeyboardButton(text="Day", callback_data="day")
    night_button = InlineKeyboardButton(text="Night", callback_data="night")
    
    # Add the buttons to the keyboard
    markup.add(day_button, night_button)
    
    return markup

def create_machine_num_keyboard():
    markup = InlineKeyboardMarkup(row_width=3)  # 3 buttons per row
    buttons = []

    # Add number buttons from 1 to 23
    for i in range(1, 24):
        buttons.append(InlineKeyboardButton(text=str(i), callback_data=f"machine_{i}"))

    # Add buttons to the keyboard
    markup.add(*buttons)

    return markup

def get_paginated_products(page=0, page_size=10):
    machine_linked = Product.objects.filter(machine__isnull=False).order_by('machine__number')
    non_machine_linked = Product.objects.filter(machine__isnull=True).order_by('name')
    combined_products = list(machine_linked) + list(non_machine_linked)
    start = page * page_size
    end = start + page_size
    products_on_page = combined_products[start:end]
    total_products = len(combined_products)
    return products_on_page, total_products


# Function to create an inline keyboard for paginated products
def create_product_keyboard(page=0):
    products, total_products = get_paginated_products(page=page)
    markup = InlineKeyboardMarkup()

    # Add product buttons to the keyboard in rows of 3
    row = []
    for product in products:
        row.append(InlineKeyboardButton(text=product.name, callback_data=f"product_{product.id}"))
        if len(row) == 2:
            markup.add(*row)
            row = []
    if row:
        markup.add(*row)
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text="<", callback_data=f"page_{page - 1}"))

    buttons.append(InlineKeyboardButton(text=f"{page + 1}", callback_data="current_page"))
    
    if (page + 1) * 6 < total_products:  # Add '>' button if there are more products
        buttons.append(InlineKeyboardButton(text=">", callback_data=f"page_{page + 1}"))

    # Add pagination buttons as the last row
    markup.add(*buttons)
    
    return markup

def get_paginated_materials(page=0, page_size=6):
    # Fetch products for the current page
    start = page * page_size
    end = start + page_size
    materials = Material.objects.all()[start:end]
    total_materials = Material.objects.count()
    return materials, total_materials

def create_material_keyboard(page=0):
    materials, total_materials = get_paginated_materials(page=page)
    markup = InlineKeyboardMarkup()

    # Add product buttons to the keyboard in rows of 3
    row = []
    for material in materials:
        row.append(InlineKeyboardButton(text=material.name, callback_data=f"material_{material.id}"))
        if len(row) == 2:
            markup.add(*row)  # Add the current row to the keyboard
            row = []  # Reset the row for the next set of buttons
    
    # Add any remaining buttons in the last row
    if row:
        markup.add(*row)
    
    # Determine if pagination buttons are needed
    buttons = []
    if page > 0:  # Add '<' button if not on the first page
        buttons.append(InlineKeyboardButton(text="<", callback_data=f"m-page_{page - 1}"))
    
    # Add 'x' button as a placeholder for current page number
    buttons.append(InlineKeyboardButton(text=f"{page + 1}", callback_data="current_page"))
    
    if (page + 1) * 6 < total_materials:  # Add '>' button if there are more products
        buttons.append(InlineKeyboardButton(text=">", callback_data=f"m-page_{page + 1}"))

    # Add pagination buttons as the last row
    markup.add(*buttons)
    
    return markup

def get_paginated_materials_for_product(product, page=0, page_size=6):
    # Fetch materials for the current product
    start = page * page_size
    end = start + page_size
    materials = Material.objects.filter(products=product)[start:end]
    total_materials = Material.objects.filter(products=product).count()
    return materials, total_materials


def create_material_keyboard_for_product(product, page=0):
    materials, total_materials = get_paginated_materials_for_product(product, page=page)
    markup = InlineKeyboardMarkup()

    # Add material buttons to the keyboard in rows of 2
    row = []
    for material in materials:
        row.append(InlineKeyboardButton(text=material.name, callback_data=f"material_{material.id}"))
        if len(row) == 2:
            markup.add(*row)  # Add the current row to the keyboard
            row = []  # Reset the row for the next set of buttons
    
    # Add any remaining buttons in the last row
    if row:
        markup.add(*row)
    
    # Pagination buttons
    buttons = []
    if page > 0:  # Add '<' button if not on the first page
        buttons.append(InlineKeyboardButton(text="<", callback_data=f"m-page_{page - 1}"))
    
    # Add 'x' button as a placeholder for current page number
    buttons.append(InlineKeyboardButton(text=f"{page + 1}", callback_data="current_page"))
    
    if (page + 1) * 6 < total_materials:  # Add '>' button if there are more materials
        buttons.append(InlineKeyboardButton(text=">", callback_data=f"m-page_{page + 1}"))

    # Add pagination buttons as the last row
    markup.add(*buttons)
    
    return markup


def create_days_info_kb(year=None, month=None):
    if year is None or month is None:
        today = datetime.now()
        year = today.year
        month = today.month
    markup = types.InlineKeyboardMarkup(row_width=7)
    month_name = datetime(year, month, 1).strftime('%B %Y')
    title = types.InlineKeyboardButton(f"--- {month_name} ---", callback_data="ignore")
    markup.add(title)
    first_day = datetime(year, month, 1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    buttons = [types.InlineKeyboardButton(
        text=str(day),
        callback_data=f"info_{day:02d}.{month:02d}.{year}"
    ) for day in range(1, last_day.day + 1)]
    markup.add(*buttons)
    prev_month = (first_day - timedelta(days=1)).replace(day=1)
    next_month = (last_day + timedelta(days=1)).replace(day=1)
    navigation = [
        types.InlineKeyboardButton("<", callback_data=f"infnav_{prev_month.year}_{prev_month.month}"),
        types.InlineKeyboardButton("x", callback_data="ignore"),
        types.InlineKeyboardButton(">", callback_data=f"infnav_{next_month.year}_{next_month.month}")
    ]
    markup.add(*navigation)
    return markup


def create_confirmation_keyboard1(id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Yes", callback_data=f"confirm1_yes_{id}"),
        InlineKeyboardButton("No", callback_data="confirm1_no")
    )
    return markup