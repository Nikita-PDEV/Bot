import logging  
import nest_asyncio  
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile  
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters  
import asyncio  
import os
import random  

# Применение nest_asyncio  
nest_asyncio.apply()  

# Включение логирование  
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)  
logger = logging.getLogger(__name__)  

# Вопросы викторины с уровнями сложности  
questions = {  
    'easy': [  
        {  
            "question": "Какое ваше любимое время года?",  
            "options": ["Зима", "Весна", "Лето", "Осень"],  
        },  
        {  
            "question": "Какой ваш любимый вид спорта?",  
            "options": ["Футбол", "Теннис", "Плавание", "Бег"],  
        },  
        {  
            "question": "Какое животное вам нравится больше всего?",  
            "options": ["Кошка", "Собака", "Попугай", "Крыса"],  
        },  
        {  
            "question": "Какой ваш любимый цвет?",  
            "options": ["Красный", "Синий", "Зеленый", "Желтый"],  
        },  
    ],  
    'medium': [  
        {  
            "question": "Какое ваше любимое животное?",  
            "options": ["Кошка", "Собака", "Лев", "Слон"],  
        },  
        {  
            "question": "Какой вид спорта вам нравится?",  
            "options": ["Футбол", "Теннис", "Хоккей", "Гимнастика"],  
        },  
        {  
            "question": "Какое ваше любимое животное в дикой природе?",  
            "options": ["Тигр", "Жираф", "Крокодил", "Зебра"],  
        },  
        {  
            "question": "Какое ваше любимое морское существо?",  
            "options": ["Дельфин", "Краб", "Лосось", "Медуза"],  
        },  
    ],  
}  

# Результаты викторины с картинками  
results = {  
    1: ("Ваше тотемное животное - Лев! Он символизирует силу и мужество.", "images/lion.jpg"),  
    2: ("Ваше тотемное животное - Слон! Он олицетворяет мудрость и терпение.", "images/elephant.jpg"),  
    3: ("Ваше тотемное животное - Обезьяна! Она символизирует игривость и ум.", "images/monkey.jpg"),  
    4: ("Ваше тотемное животное - Панда! Она олицетворяет мир и спокойствие.", "images/panda.jpg"),  
    5: ("Ваше тотемное животное - Тигр! Он символизирует смелость и силу.", "images/tiger.jpg"),  
    6: ("Ваше тотемное животное - Лисица! Она олицетворяет хитрость и ум.", "images/fox.jpg"),  
    7: ("Ваше тотемное животное - Орёл! Он олицетворяет надежду и свободу.", "images/eagle.jpg"),  
    8: ("Ваше тотемное животное - Волк! Он символизирует верность и доверие.", "images/wolf.jpg"),  
}  

care_program_info = '''Возьмите животное под опеку! 
Участие в программе «Клуб друзей зоопарка» — это помощь в содержании наших обитателей, 
а также ваш личный вклад в дело сохранения биоразнообразия Земли и развитие нашего зоопарка. 
Основная задача Московского зоопарка с самого начала его существования это — сохранение биоразнообразия планеты. 
Когда вы берете под опеку животное, вы помогаете нам в этом благородном деле. 
При нынешних темпах развития цивилизации к 2050 году с лица Земли могут исчезнуть около 10 000 биологических видов. 
Московский зоопарк вместе с другими зоопарками мира делает все возможное, чтобы сохранить их. 
Если вы хотите узнать дополнительную информацию, просмотрите информацию на сайте \nhttps://moscowzoo.ru/about/guardianship 
или свяжитесь с нами. 
Контактная информация: Опекунство \n+7 (962) 971-38-75 \nzoofriends@moscowzoo.ru.'''

contact_info = "Контактная информация:\nYou can reach us at contact@example.com."  

# Начальная команда  
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    await update.message.reply_text("Добро пожаловать в викторину по определению тотемного животного! Напишите /quiz, чтобы начать!")  

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    keyboard = [[InlineKeyboardButton("Лёгкий уровень", callback_data='easy'),
                InlineKeyboardButton("Средний уровень", callback_data='medium')]] 
    reply_markup = InlineKeyboardMarkup(keyboard)  
    await update.message.reply_text("Выберите уровень сложности:", reply_markup=reply_markup)  

# Начало викторины на основе выбранного уровня  
async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    query = update.callback_query  
    await query.answer()  
    level = query.data  
    context.user_data["quiz_level"] = level  # Сохраняем уровень сложности в контексте пользователя
    await ask_question(query.message, context, questions[level], 0)  # Запускаем вопросы с индексом 0  

# Задаем вопрос  
async def ask_question(message, context, question_set, question_index) -> None:  
    if question_index < len(question_set):  
        question = question_set[question_index]  
        options = question["options"]  
        keyboard = [[InlineKeyboardButton(option, callback_data=str(question_index)) for option in options]]  
        reply_markup = InlineKeyboardMarkup(keyboard)  
        await message.reply_text(question["question"], reply_markup=reply_markup)  
    else:  
        await message.reply_text("Это были все вопросы! Подсчитываем ваши результаты...")  
        await calculate_score(message)  # Подсчитываем и показываем результаты  

# Обработка ответа на вопрос  
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    query = update.callback_query  
    question_index = int(query.data)  
    level = context.user_data.get("quiz_level")  # Получаем уровень сложности из контекста  

    if level is None:  
        await query.answer("Уровень сложности не установлен. Пожалуйста, начните викторину заново.")  
        return  

    question_set = questions[level]    

    # Увеличение индекса для следующего вопроса  
    context.user_data["answered_questions"] = context.user_data.get("answered_questions", 0) + 1  
    await ask_question(query.message, context, question_set, question_index + 1)  

# Подсчет результата викторины  
async def calculate_score(message) -> None:  
    # Использование случайного значения от 1 до 8
    score = random.randint(1, 8)  # Случайный выбор от 1 до 8
    animal_result = results.get(score, results[8])  # Выбор тотемного животного в зависимости от счёта  

    # Отладочное сообщение о выборе результирующего животного
    logger.info(f"Score: {score}, Animal result: {animal_result[0]}, Image path: {animal_result[1]}")

    # Проверка существования файла изображения
    image_path = animal_result[1]
    if os.path.exists(image_path):
        logger.info(f"Image exists at: {image_path}, attempting to send the image.")
        try:
            with open(image_path, 'rb') as photo:  # Открываем файл в бинарном режиме
                await message.reply_photo(photo=photo, caption=animal_result[0])
            logger.info("Image sent successfully.")
            
            # Сообщение для отправки
            share_text = f"Я прошел викторину о тотемных животных и мое тотемное животное - {animal_result[0]}! \nПопробуйте свою удачу здесь: [@Currency256Bot](https://t.me/Currency256Bot)"

            # Кнопка для отправки
            keyboard = [[InlineKeyboardButton("Поделиться с друзьями", url=f"https://t.me/share/url?url={share_text}")]]

            # Генерация кнопки отправки
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.reply_text("Если хотите поделиться результатом с друзьями:", reply_markup=reply_markup)
            await message.reply_text("Если хотите пройти викторину снова, напишите /quiz")
            await message.reply_text("Если вы хотите узнать о программе опеки над животными, напишите /info")  # Добавляем ссылку на команду /info
            
            return  # Прерывание выполнения функции
        
        except Exception as e:
            logger.error(f"Error while sending photo: {e}")
            await message.reply_text("Произошла ошибка при отправке изображения.")
    else:
        logger.warning(f"Image not found at: {image_path}")
        await message.reply_text("Извините, изображение не найдено. Попробуйте ещё раз.")
        
    # Добавление опции для повторного прохождения викторины
    await message.reply_text("Если хотите пройти викторину снова, напишите /quiz")  
    await message.reply_text("Если вы хотите узнать о программе опеки над животными, напишите /info")  # Добавляем ссылку на команду /info


# Команда для получения информации о программе опеки  
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    await update.message.reply_text(care_program_info)  

# Команда для получения контактной информации  
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    await update.message.reply_text(contact_info)  

# Команда для сбора отзывов  
async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    await update.message.reply_text("Пожалуйста, напишите ваш отзыв. После завершения напишите /done.")  

# Обработка пользовательского отзыва  
async def collect_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    feedback_text = update.message.text  
    logger.info(f"Received feedback: {feedback_text}")  
    await update.message.reply_text("Спасибо за ваш отзыв! Мы ценим ваше мнение.")  

# Команда для завершения сбора отзывов  
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    await update.message.reply_text("Вы завершили отправку отзывов. Спасибо!")  

# Главная функция приложения  
async def main():  
    application = ApplicationBuilder().token('').build()  # Убедитесь, что вставили свой токен.  

    # Добавление обработчиков команд  
    application.add_handler(CommandHandler("start", start))  
    application.add_handler(CommandHandler("quiz", quiz))  
    application.add_handler(CommandHandler("info", info))  
    application.add_handler(CommandHandler("contact", contact))  
    application.add_handler(CommandHandler("feedback", feedback))  
    application.add_handler(CommandHandler("done", done))  
    application.add_handler(CallbackQueryHandler(start_quiz, pattern='^(easy|medium)$'))  
    application.add_handler(CallbackQueryHandler(answer))  
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_feedback))  # Обработчик для ввода отзывов  

    # Запуск бота  
    await application.run_polling()  

# Точка входа в программу  
if __name__ == '__main__':  
    try:  
        asyncio.run(main())  
    except Exception as e:  
        logging.error(f'An error occurred: {e}')  