from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
from telegram.ext import ConversationHandler
from dotenv import load_dotenv

import os
import shutil
from TerraYolo.TerraYolo import TerraYoloV5             # загружаем фреймворк TerraYolo

# возьмем переменные окружения из .env
load_dotenv()
# загружаем токен бота
TOKEN =  os.environ.get("TOKEN")

# инициализируем класс YOLO
WORK_DIR = r'C:\Users\stavo\PycharmProjects\DataScienceCourse\Lesson20'
os.makedirs(WORK_DIR, exist_ok=True)
yolov5 = TerraYoloV5(work_dir=WORK_DIR)

CHOOSING_FIRST, CHOOSING_SECOND, RECEIVING_PHOTO = range(3)

user_data = {}

async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [[InlineKeyboardButton("Coeff 0.01", callback_data='0.01'),
                 InlineKeyboardButton("Coeff 0.5", callback_data='0.5'),
                 InlineKeyboardButton("Coeff 0.99", callback_data='0.99')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose the coeff:', reply_markup=reply_markup)
    return CHOOSING_FIRST

async def first_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_data[query.from_user.id] = {'first_choice': query.data}

    keyboard = [
        [InlineKeyboardButton("Persons", callback_data='0'),
         InlineKeyboardButton("Cars", callback_data='2'),
         InlineKeyboardButton("Backpacks", callback_data='24')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text='Choose the object:', reply_markup=reply_markup)
    return CHOOSING_SECOND

async def second_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_data[query.from_user.id]['second_choice'] = query.data
    await query.edit_message_text(text='Now send me a photo.')
    return RECEIVING_PHOTO

# async def handle_photo(update: Update, context: CallbackContext) -> int:
#     # user_id = update.message.from_user.id
#     # photo_file = await update.message.photo[-1].get_file()
#     # photo_path = f'photo_{user_id}.jpg'
#
#     # функция обработки изображения
#     # удаляем папку images с предыдущим загруженным изображением и папку runs с результатом предыдущего распознавания
#     user_id = update.message.from_user.id
#     try:
#         shutil.rmtree('images')
#         shutil.rmtree(f'{WORK_DIR}/yolov5/runs')
#     except:
#         pass
#
#     my_message = await update.message.reply_text('Мы получили от тебя фотографию. Идет распознавание объектов...')
#     # получение файла из сообщения
#     new_file = await update.message.photo[-1].get_file()
#
#     # имя файла на сервере
#     os.makedirs('images', exist_ok=True)
#     image_name = str(new_file['file_path']).split("/")[-1]
#     image_path = os.path.join('images', image_name)
#     # скачиваем файл с сервера Telegram в папку images
#     await new_file.download_to_drive(image_path)
#
#     # создаем словарь с параметрами
#     test_dict = dict()
#     test_dict[
#         'weights'] = 'yolov5x.pt'  # Самые сильные веса yolov5x.pt, вы также можете загрузить версии: yolov5n.pt, yolov5s.pt, yolov5m.pt, yolov5l.pt (в порядке возрастания)
#     print(user_data[user_id]['first_choice'])
#     test_dict['source'] = 'images'  # папка, в которую загружаются присланные в бота изображения
#     test_dict['conf'] = user_data[user_id]['first_choice']  # порог распознавания
#     test_dict['classes'] = user_data[user_id]['second_choice'] #'50 39'        # классы, которые будут распознаны
#
#     # вызов функции detect из класса TerraYolo)
#     yolov5.run(test_dict, exp_type='test')
#
#     # удаляем предыдущее сообщение от бота
#     await context.bot.deleteMessage(message_id=my_message.message_id,
#                                     # если не указать message_id, то удаляется последнее сообщение
#                                     chat_id=update.message.chat_id)  # если не указать chat_id, то удаляется последнее сообщение
#
#     # отправляем пользователю результат
#     await update.message.reply_text('Распознавание объектов завершено')  # отправляем пользователю результат
#     await update.message.reply_photo(
#         f"{WORK_DIR}/yolov5/runs/detect/exp/{image_name}")  # отправляем пользователю результат изображение
#
#     return ConversationHandler.END

async def handle_photo2(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id

    # Удаление предыдущих изображений и результатов
    try:
        shutil.rmtree('images')
        shutil.rmtree(f'{WORK_DIR}/yolov5/runs')
    except:
        pass

    my_message = await update.message.reply_text('Мы получили от тебя фотографию. Идет распознавание объектов...')

    # Определение, является ли сообщение фотографией или документом
    if update.message.photo:
        # Получение сжатой фотографии
        new_file = await update.message.photo[-1].get_file()
        image_name = str(new_file['file_path']).split("/")[-1]
    elif update.message.document and update.message.document.mime_type.startswith('image/'):
        # Получение несжатого изображения, отправленного как документ
        new_file = await update.message.document.get_file()
        image_name = update.message.document.file_name
    else:
        await update.message.reply_text('Пожалуйста, отправьте изображение в формате фотографии или документа.')
        return ConversationHandler.END

    # Создание директории для изображений
    os.makedirs('images', exist_ok=True)
    image_path = os.path.join('images', image_name)

    # Скачивание файла
    await new_file.download_to_drive(image_path)

    # Создание словаря с параметрами
    test_dict = {
        'weights': 'yolov5s.pt',
        'source': 'images',
        'conf': user_data[user_id]['first_choice'],
        'classes': user_data[user_id]['second_choice']
    }

    # Вызов функции detect из класса TerraYolo
    yolov5.run(test_dict, exp_type='test')

    # Удаление предыдущего сообщения от бота
    await context.bot.delete_message(message_id=my_message.message_id, chat_id=update.message.chat_id)

    # Отправка пользователю результата
    await update.message.reply_text('Распознавание объектов завершено')
    # await update.message.reply_photo(f"{WORK_DIR}/yolov5/runs/detect/exp/{image_name}")
    print((f"{WORK_DIR}/yolov5/runs/detect/exp/{image_name}"))
    return ConversationHandler.END


async def handle_document(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    document = update.message.document

    if document.mime_type.startswith('image/'):
        photo_file = await document.get_file()
        photo_path = f'document_{user_id}.jpg'
        await photo_file.download_to_drive(photo_path)

        process_photo(photo_path, user_data[user_id]['first_choice'], user_data[user_id]['second_choice'])
        await update.message.reply_text('Document received and processed!')
    else:
        await update.message.reply_text('Please send an image file.')
    return ConversationHandler.END

def process_photo(photo_path: str, first_choice: str, second_choice: str):
    # Placeholder function to process the photo
    print(f"Processing photo {photo_path} with choices {first_choice} and {second_choice}")

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_FIRST: [CallbackQueryHandler(first_choice)],
            CHOOSING_SECOND: [CallbackQueryHandler(second_choice)],
            RECEIVING_PHOTO: [
                MessageHandler(filters.PHOTO, handle_photo2),
                MessageHandler(filters.Document.ALL, handle_photo2)
            ]
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
