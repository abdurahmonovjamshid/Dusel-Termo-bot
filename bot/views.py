from django.shortcuts import render

# Create your views here.

import json
import traceback
from django.http import HttpResponse

import requests
import telebot
import telegraph
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from django.utils import timezone
from conf.settings import ADMINS, CHANNEL_ID, HOST, TELEGRAM_BOT_TOKEN, ADMINS2

from .buttons.default import cencel, main_button, get_back
from .buttons.inline import create_days_keyboard, create_product_keyboard, urlkb, create_day_night_keyboard, create_days_info_kb, create_machine_num_keyboard, create_material_keyboard_for_product
from .models import TgUser
from .services.addcar import (add_product, add_material, add_measure, add_waste, add_defect, add_quantity, create_excel_report)
from .services.steps import USER_STEP
from bot.models import Product, Material, Report, Machine
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
from datetime import datetime


@csrf_exempt
def telegram_webhook(request):
    try:
        if request.method == 'POST':
            update_data = request.body.decode('utf-8')
            update_json = json.loads(update_data)
            update = telebot.types.Update.de_json(update_json)

            if update.message:
                tg_user = update.message.from_user
                telegram_id = tg_user.id
                first_name = tg_user.first_name
                last_name = tg_user.last_name
                username = tg_user.username
                is_bot = tg_user.is_bot
                language_code = tg_user.language_code

                deleted = False

                tg_user_instance, _ = TgUser.objects.update_or_create(
                    telegram_id=telegram_id,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'username': username,
                        'is_bot': is_bot,
                        'language_code': language_code,
                        'deleted': deleted,
                    }
                )

            try:
                if update.my_chat_member.new_chat_member.status == 'kicked':
                    telegram_id = update.my_chat_member.from_user.id
                    user = TgUser.objects.get(telegram_id=telegram_id)
                    user.deleted = True
                    user.save()
            except:
                pass

            bot.process_new_updates(
                [telebot.types.Update.de_json(request.body.decode("utf-8"))])

        return HttpResponse("ok")
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        return HttpResponse("error")


@bot.message_handler(commands=['start'])
def start_handler(message):
    try:
        user = TgUser.objects.get(telegram_id=message.from_user.id)
        user.step = USER_STEP['DEFAULT']
        user.save()
        response_message = f"Salom, {message.from_user.full_name}!😊 \nDusel Termoplast ishlab chiqarish"

        # Send the response message back to the user
        msg = bot.send_photo(chat_id=message.chat.id, photo='https://72.uz/image/catalog/CATALOG/elektrika/lampi-projectori-paneli/Led-lampi/E27/Dusel/tomchi_lampochkalar.png',
                       caption=response_message, reply_markup=main_button)
        Report.objects.filter(is_confirmed=False, user=user).delete()
        bot.delete_message(chat_id=message.chat.id, message_id=user.edit_msg)
    
    except Exception as e:
        print(e)



@bot.message_handler(regexp="📝 Ma'lumot qo'shish")
def cm_start(message):
    try:
        user = TgUser.objects.get(telegram_id=message.from_user.id)
        if str(user.telegram_id) in ADMINS:
            markup = create_days_keyboard()
            bot.send_message(message.chat.id, "Ma'lumot kiritish boshlandi...", reply_markup=get_back)
            msg = bot.send_message(message.chat.id, "Choose a day:", reply_markup=markup)
            user.edit_msg = msg.id 
            user.save()
        else:
            bot.send_message(chat_id=message.from_user.id,
                             text="🚫 Sizda ruxsat yo'q")
            TgUser.objects.filter(telegram_id=message.chat.id).update(
                step=USER_STEP['ADD_DAY'], edit_msg=msg.id)
    except Exception as e:
        print(e)


@bot.message_handler(regexp="📊 Ma'lumot olish")
def cm_start(message):
    try:
        user = TgUser.objects.get(telegram_id=message.from_user.id)
        if str(user.telegram_id) in ADMINS2:
            markup = create_days_info_kb()
            msg = bot.send_message(message.chat.id, "Choose a day:", reply_markup=markup)
            user.edit_msg = msg.id 
            user.save()
        else:
            bot.send_message(chat_id=message.from_user.id,
                             text="🚫 Sizda ruxsat yo'q")
            TgUser.objects.filter(telegram_id=message.chat.id).update(
                step=USER_STEP['REPORT'], edit_msg=msg.id)
    except Exception as e:
        print(e)


# Handler for button presses
@bot.callback_query_handler(func=lambda call: call.data.startswith('nav_') or call.data.startswith('date_'))
def handle_navigation(call):
    user = TgUser.objects.get(telegram_id=call.from_user.id)
    if call.data.startswith('nav_'):
        # Extract year and month from the callback data
        _, year, month = call.data.split('_')
        year, month = int(year), int(month)
        # Create a new keyboard for the requested month
        markup = create_days_keyboard(year, month)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif call.data.startswith('date_'):
        # Extract the selected date
        date_str = call.data.split('_')[1]
        bot.answer_callback_query(call.id, f"Selected date: {date_str}")
        markup = create_day_night_keyboard()
        edit_message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Report\n{date_str}\n\nchoose the shift:", parse_mode='html', reply_markup=markup)
        date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
        report = Report.objects.create(date=date_obj, user=user)
        TgUser.objects.filter(telegram_id=call.from_user.id).update(
                step=USER_STEP['ADD_SHIFT'], edit_msg=edit_message.id)
        

import os

TEMP_DIR = os.path.join(os.getcwd(), 'temp_files')
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
    
    
@bot.callback_query_handler(func=lambda call: call.data.startswith('infnav_') or call.data.startswith('info_'))
def handle_navigation(call):
    try:
        user = TgUser.objects.get(telegram_id=call.from_user.id)
        
        if call.data.startswith('infnav_'):
            _, year, month = call.data.split('_')
            year, month = int(year), int(month)
            markup = create_days_info_kb(year, month)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        
        elif call.data.startswith('info_'):
            date_str = call.data.split('_')[1]
            selected_date = datetime.strptime(date_str, '%d.%m.%Y').date()

            # Retrieve reports for the selected date and user
            reports = Report.objects.filter(date=selected_date).order_by('default_value', 'machine_num')

            if reports.exists():
                # Generate Excel file and save it to a temporary location
                file_name = f"report_{selected_date}.xlsx"
                file_path = os.path.join(TEMP_DIR, file_name)
                create_excel_report(reports, file_path)

                # Send the file using its path
                with open(file_path, 'rb') as file:
                    bot.send_document(
                        chat_id=call.message.chat.id, 
                        document=file, 
                        caption=f"Reports for {selected_date.strftime('%d.%m.%Y')}"
                    )

                # Delete the file after sending
                os.remove(file_path)
            else:
                bot.answer_callback_query(call.id, f"No reports found for {date_str}")

            bot.answer_callback_query(call.id, f"Selected date: {date_str}")
    except Exception as e:
        bot.answer_callback_query(call.id, f"{date_str} sana blan ma'lumot kiritilmoqda kuting")


# Handler to ignore other buttons (like month title and x button)
@bot.callback_query_handler(func=lambda call: call.data == "ignore")
def ignore_callback(call):
    bot.answer_callback_query(call.id, text="")
    
    
@bot.callback_query_handler(func=lambda call: call.data.startswith('day') or call.data.startswith('night'))
def day_night_callback_handler(call):
    try:
        user = TgUser.objects.get(telegram_id=call.from_user.id)
        report = Report.objects.get(is_confirmed=False, user=user)
        
        # Handle day or night selection
        if call.data == "day":
            report.default_value = 'Kun'
        elif call.data == "night":
            report.default_value = 'Tun'
        
        report.save()

        # Ask the user to select a machine number after choosing day/night
        markup = create_machine_num_keyboard()
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Report\n{report.date} - {report.default_value}\n\n Select a machine number:",
            reply_markup=markup,
            parse_mode='html'
        )
        TgUser.objects.filter(telegram_id=call.from_user.id).update(
                step=USER_STEP['ADD_MACHINE'])
    except Exception as e:
        print(e)

        
@bot.callback_query_handler(func=lambda call: call.data.startswith('machine_'))
def machine_num_callback_handler(call):
    try:
        user = TgUser.objects.get(telegram_id=call.from_user.id)
        report = Report.objects.get(is_confirmed=False, user=user)  # Get the report for the user
        
        # Extract machine number from the callback data
        machine_num = int(call.data.split("_")[1])

        # Update the report's machine number
        report.machine_num = machine_num
        report.save()

        # Acknowledge the user's selection and move to the next step
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Report\n{report.date} - {report.default_value}\n\n Machine Number: {report.machine_num}\n\n Choose or search Product:",
            reply_markup=create_product_keyboard(),  # Assuming next step is product selection
            parse_mode='html'
        )
        TgUser.objects.filter(telegram_id=call.from_user.id).update(
                step=USER_STEP['ADD_PRODUCT'])
    except Exception as e:
        print(e)

        

@bot.callback_query_handler(func=lambda call: call.data.startswith("product_") or call.data.startswith("page_"))
def handle_callback(call):
    try:
        user = TgUser.objects.get(telegram_id=call.from_user.id)
        report = Report.objects.get(is_confirmed=False, user=user)

        # Handle product selection
        if call.data.startswith("product_"):
            product_id = int(call.data.split("_")[1])  
            selected_product = Product.objects.get(id=product_id)
            report.product = selected_product
            report.save()
            
            machine = Machine.objects.filter(number=report.machine_num).first()
            machine.product = selected_product
            machine.save()
            
            markup = create_material_keyboard_for_product(report.product)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"Report\n{report.date} - {report.default_value}\n\n Machine Number: {report.machine_num}\n\nProduct: {report.product.name}\n\nChoose a material:",
                reply_markup=markup,
                parse_mode='html'
            )
            TgUser.objects.filter(telegram_id=call.from_user.id).update(step=USER_STEP['ADD_MATERIAL'])
            
        elif call.data.startswith("page_"):
            page = int(call.data.split("_")[1])
            markup = create_product_keyboard(page=page)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)

    except Exception as e:
        print(e)

            
@bot.callback_query_handler(func=lambda call: call.data.startswith('material_') or call.data.startswith('m-page_'))
def material_selection_handler(call):
    try:
        # Assume we have the report and product already selected
        user = TgUser.objects.get(telegram_id=call.from_user.id)
        report = Report.objects.get(is_confirmed=False, user=user)  # Get the report object
        product = report.product  # Get the product associated with the report

        # Handle pagination (moving between pages)
        if call.data.startswith("m-page_"):
            page = int(call.data.split("_")[1])
            markup = create_material_keyboard_for_product(product, page=page)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        
        # Handle material selection
        elif call.data.startswith("material_"):
            material_id = int(call.data.split("_")[1])
            material = Material.objects.get(id=material_id)
            
            # Update the report's material
            report.material = material
            report.save()
            
            # Confirm the selection to the user
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"Report\n{report.date} - {report.default_value}\n\n Machine Number: {report.machine_num}Product: {report.product.name}Material: {report.material.name}\n\nTermoplast vazni:",
                parse_mode='html'
            )
            TgUser.objects.filter(telegram_id=call.from_user.id).update(step=USER_STEP['ADD_MEASURE'])
    
    except Exception as e:
        print(e)
        
@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_') or call.data.startswith('cancel_'))
def material_selection_handler(call):
    try:
        user = TgUser.objects.get(telegram_id=call.from_user.id)
        report = Report.objects.get(is_confirmed=False, user=user)
        bot.answer_callback_query(call.id, f"Report Saved")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=None)
        bot.send_message(chat_id=call.message.chat.id, text='malumot saqlandi')
        if call.data.startswith("confirm_"):
            confirmed_report = Report.objects.filter(
                date=report.date,
                default_value=report.default_value,
                machine_num=report.machine_num,
                product=report.product,
                is_confirmed=True
            ).first()

            if confirmed_report:
                confirmed_report.termoplast_measure += report.termoplast_measure or 0
                confirmed_report.defect_measure += report.defect_measure or 0
                confirmed_report.waste_measure += report.waste_measure or 0
                confirmed_report.quantity += report.quantity or 0
                confirmed_report.save()
                report.product = None
                report.material = None
                report.termoplast_measure = 0
                report.defect_measure = 0
                report.waste_measure = 0
                report.quantity = 0
                report.save()
            else:
                report.is_confirmed = True
                report.save()
                report = Report.objects.create(date=report.date, default_value=report.default_value, user=user)
            msg = bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Report\n{report.date} - {report.default_value}\n\n Select a machine number:",
            reply_markup=create_machine_num_keyboard(),
            parse_mode='html'
        )
            user.edit_msg = msg.id
            user.step=USER_STEP['ADD_MACHINE']
            user.save()
        elif call.data.startswith("cancel_"):
            pass
    
    except Exception as e:
        print(e)
        
        
@bot.message_handler(func=lambda message: message.text == '⬅️ ortga')  # This catches the "Back" button press
def get_step_back(message):
    try:
        user = TgUser.objects.get(telegram_id=message.from_user.id)
        
        # Prevent going back beyond the first step
        if user.step > USER_STEP['DEFAULT']:
            # Decrement the step
            user.step -= 1
            user.save()

            # Handle each step case
            report = Report.objects.get(is_confirmed=False, user=user)
            if user.step == USER_STEP['ADD_DAY']:
                report.delete()
                # Step back to day selection
                markup = create_days_keyboard()
                bot.edit_message_text(chat_id=message.chat.id, message_id=user.edit_msg,
                                      text="Choose a day:", reply_markup=markup)
            elif user.step == USER_STEP['ADD_SHIFT']:
                # Step back to shift selection
                markup = create_day_night_keyboard()
                bot.edit_message_text(chat_id=message.chat.id, message_id=user.edit_msg,
                                      text=f"Report\n{report.date}\nChoose the shift:", reply_markup=markup)
            elif user.step == USER_STEP['ADD_MACHINE']:
                # Step back to machine selection
                markup = create_machine_num_keyboard()
                bot.edit_message_text(chat_id=message.chat.id, message_id=user.edit_msg,
                                      text=f"Report\n{report.date} - {report.default_value}\n\nSelect a machine number:",
                                      reply_markup=markup)
            elif user.step == USER_STEP['ADD_PRODUCT']:
                # Step back to product selection
                markup = create_product_keyboard()
                bot.edit_message_text(chat_id=message.chat.id, message_id=user.edit_msg,
                                      text=f"Report\n{report.date} - {report.default_value}\nMachine Number: {report.machine_num}\n\n Choose or search Product:", reply_markup=markup)
            elif user.step == USER_STEP['ADD_MATERIAL']:
                # Step back to material selection
                markup = create_material_keyboard_for_product(report.product)
                bot.edit_message_text(chat_id=message.chat.id, message_id=user.edit_msg,
                                      text=f"Report\n{report.date} - {report.default_value}\nMachine Number: {report.machine_num}\n\nProduct: {report.product.name}Choose a material:", reply_markup=markup)
            elif user.step == USER_STEP['ADD_MEASURE']:
                # Step back to entering the termoplast weight
                bot.edit_message_text(chat_id=message.chat.id, message_id=user.edit_msg,
                                      text=f"Report\n{report.date} - {report.default_value}\n\n Machine Number: {report.machine_num}Product: {report.product.name}Material: {report.material.name}\n\nTermoplast vazni:")
            elif user.step == USER_STEP['ADD_WASTE']:
                # Step back to entering the waste weight
                bot.edit_message_text(chat_id=message.chat.id, message_id=user.edit_msg,
                                      text=f"Report\n{report.date} - {report.default_value}\nMachine Number: {report.machine_num}\n\nProduct: {report.product.name}\nMaterial: {report.material.name}\n\nTermoplast vazni: {report.termoplast_measure}\n\nBrak vazni:")
            elif user.step == USER_STEP['ADD_DEFECT']:
                # Step back to entering the defect weight
                bot.edit_message_text(chat_id=message.chat.id, message_id=user.edit_msg,
                                      text=f"Report\n{report.date} - {report.default_value}\nMachine Number: {report.machine_num}\n\nProduct: {report.product.name}\nMaterial: {report.material.name}\n\nTermoplast vazni: {report.termoplast_measure}\n\nBrak vazni: {report.waste_measure}\n\nAtxod vaznini kiriting:")
            
            elif user.step == USER_STEP['ADD_QUANTITY']:
                # Step back to entering the product quantity
                bot.edit_message_text(chat_id=message.chat.id, message_id=user.edit_msg,
                                      text=f"Report\n{report.date} - {report.default_value}\nMachine Number: {report.machine_num}\n\nProduct: {report.product.name}\nMaterial: {report.material.name}\n\nTermoplast vazni: {report.termoplast_measure}\n\nBrak vazni: {report.waste_measure}\n\nAtxod vaznini: {report.defect_measure}\n\nMaxsulot sonini kiriting: ")

            # Optionally delete the "Back" message
            bot.delete_message(chat_id=message.chat.id, message_id=message.id)
        else:
            bot.delete_message(chat_id=message.chat.id, message_id=message.id)
            # If at the initial step, just inform the user
            bot.send_message(chat_id=message.chat.id, text="Malumot kiritish bekor qilindi", reply_markup=main_button)
            bot.delete_message(chat_id=message.chat.id, message_id=user.edit_msg)

    except Exception as e:
        # Log the error for debugging
        print(f"Error occurred: {e}")
        bot.send_message(chat_id=message.chat.id, text="Malumot kiritish bekor qilindi", reply_markup=main_button)
        bot.delete_message(chat_id=message.chat.id, message_id=user.edit_msg)

        
@bot.message_handler(content_types=['text', 'contact', 'photo'])
def text_handler(message):
    try:
        switcher = {
            USER_STEP['ADD_PRODUCT']: add_product,
            USER_STEP['ADD_MATERIAL']: add_material,
            USER_STEP['ADD_MEASURE']: add_measure,
            USER_STEP['ADD_WASTE']: add_waste,
            USER_STEP['ADD_DEFECT']: add_defect,
            USER_STEP['ADD_QUANTITY']: add_quantity,
            
        }
        func = switcher.get(TgUser.objects.get(
            telegram_id=message.chat.id).step)
        if func:
            func(message, bot)
        else:
            start_handler(message)
    except Exception as e:
        # bot.send_message(313578337, f'{str(e)}')
        print(e)
        traceback.print_tb(e.__traceback__)


bot.set_webhook(url="https://"+HOST+"/webhook/")
