import os
import sqlite3
from typing import Dict, List, Optional
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Load environment variables
load_dotenv()

# Initialize bot and dispatcher
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Define states for FSM
class SteelComposition(StatesGroup):
    waiting_for_composition = State()
    waiting_for_value = State()

# Database connection
def get_db_connection():
    return sqlite3.connect('steel_database.db')

# Function to find matching steel grades
def find_matching_steels(composition: Dict[str, float]) -> List[tuple]:
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT steel_grade, specification,
           C_min, C_max, Si_min, Si_max, Mn_min, Mn_max,
           S_min, S_max, P_min, P_max, Cr_min, Cr_max,
           Ni_min, Ni_max, Cu_min, Cu_max, Mo_min, Mo_max,
           V_min, V_max, Nb_min, Nb_max, Ti_min, Ti_max,
           N_min, N_max, W_min, W_max, B_min, B_max,
           Co_min, Co_max
    FROM steel_grades
    WHERE
        C_min <= ? AND C_max >= ? AND
        Si_min <= ? AND Si_max >= ? AND
        Mn_min <= ? AND Mn_max >= ? AND
        S_min <= ? AND S_max >= ? AND
        P_min <= ? AND P_max >= ? AND
        Cr_min <= ? AND Cr_max >= ? AND
        Ni_min <= ? AND Ni_max >= ? AND
        Cu_min <= ? AND Cu_max >= ? AND
        Mo_min <= ? AND Mo_max >= ? AND
        V_min <= ? AND V_max >= ? AND
        Nb_min <= ? AND Nb_max >= ? AND
        Ti_min <= ? AND Ti_max >= ? AND
        N_min <= ? AND N_max >= ? AND
        W_min <= ? AND W_max >= ? AND
        B_min <= ? AND B_max >= ? AND
        Co_min <= ? AND Co_max >= ?
    """

    params = []
    for element in ['C', 'Si', 'Mn', 'S', 'P', 'Cr', 'Ni', 'Cu', 'Mo', 'V', 'Nb', 'Ti', 'N', 'W', 'B', 'Co']:
        value = composition.get(element, 0)
        params.extend([value, value])

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

# Function to find the closest steel grade using Euclidean distance
def find_closest_steel(composition: Dict[str, float]) -> tuple:
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT steel_grade, specification,
           C_min, C_max, Si_min, Si_max, Mn_min, Mn_max,
           S_min, S_max, P_min, P_max, Cr_min, Cr_max,
           Ni_min, Ni_max, Cu_min, Cu_max, Mo_min, Mo_max,
           V_min, V_max, Nb_min, Nb_max, Ti_min, Ti_max,
           N_min, N_max, W_min, W_max, B_min, B_max,
           Co_min, Co_max
    FROM steel_grades
    """

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    if not results:
        return None

    closest_steel = None
    min_distance = float('inf')

    for result in results:
        steel_grade, specification = result[0], result[1]

        # Calculate average composition from min/max ranges
        db_composition = {}
        for i, element in enumerate(['C', 'Si', 'Mn', 'S', 'P', 'Cr', 'Ni', 'Cu', 'Mo', 'V', 'Nb', 'Ti', 'N', 'W', 'B', 'Co']):
            min_idx = 2 + i * 2
            max_idx = min_idx + 1
            min_val = result[min_idx] or 0
            max_val = result[max_idx] or 0
            db_composition[element] = (min_val + max_val) / 2

        # Calculate Euclidean distance
        distance = 0
        for element in ['C', 'Si', 'Mn', 'S', 'P', 'Cr', 'Ni', 'Cu', 'Mo', 'V', 'Nb', 'Ti', 'N', 'W', 'B', 'Co']:
            input_val = composition.get(element, 0)
            db_val = db_composition.get(element, 0)
            distance += (input_val - db_val) ** 2
        distance = distance ** 0.5

        if distance < min_distance:
            min_distance = distance
            closest_steel = (steel_grade, specification, db_composition)

    return closest_steel

# List of elements to ask for
ELEMENTS = ['C', 'Si', 'Mn', 'S', 'P', 'Cr', 'Ni', 'Cu', 'Mo', 'V', 'Nb', 'Ti', 'N', 'W', 'B', 'Zr']

def create_composition_keyboard(composition: Dict[str, float]) -> InlineKeyboardMarkup:
    keyboard = []
    # Create rows of 2 elements each
    for i in range(0, len(ELEMENTS), 2):
        row = []
        for element in ELEMENTS[i:i+2]:
            value = composition.get(element, 0.0)
            row.append(InlineKeyboardButton(
                text=f"{element}: {value:.3f}",
                callback_data=f"edit_{element}"
            ))
        keyboard.append(row)

    # Add search and new search buttons at the bottom
    keyboard.append([
        InlineKeyboardButton(text="Поиск", callback_data="search"),
        InlineKeyboardButton(text="Сброс", callback_data="new_search")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать в бот для поиска марок стали! 🏭\n\n"
        "Я помогу вам найти марки стали на основе их химического состава.\n"
        "Используйте команду /find, чтобы начать поиск."
    )

@dp.message(Command("find"))
async def cmd_find(message: Message, state: FSMContext):
    # Initialize the composition dictionary with zeros
    composition = {element: 0.0 for element in ELEMENTS}
    await state.update_data(composition=composition)

    # Create the message with current values
    message_text = "Химический состав стали (в %):\n\n"
    message_text += "Нажмите на элемент, чтобы изменить его значение\n"

    # Create keyboard with current values
    keyboard = create_composition_keyboard(composition)

    await state.set_state(SteelComposition.waiting_for_composition)
    await message.answer(message_text, reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("edit_"))
async def process_edit(callback_query: CallbackQuery, state: FSMContext):
    element = callback_query.data.split("_")[1]
    await state.update_data(current_element=element)
    await state.set_state(SteelComposition.waiting_for_value)
    await callback_query.message.answer(f"Введите значение для {element}:")
    await callback_query.answer()

@dp.message(SteelComposition.waiting_for_value)
async def process_value(message: Message, state: FSMContext):
    try:
        value = float(message.text)
        state_data = await state.get_data()
        composition = state_data.get("composition", {})
        current_element = state_data.get("current_element")

        if current_element:
            composition[current_element] = value
            await state.update_data(composition=composition)

            # Create updated message
            message_text = "Химический состав стали (в %):\n\n"
            message_text += "Нажмите на элемент, чтобы изменить его значение\n"

            # Create keyboard with updated values
            keyboard = create_composition_keyboard(composition)

            await state.set_state(SteelComposition.waiting_for_composition)
            await message.answer(message_text, reply_markup=keyboard)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное числовое значение.")

@dp.callback_query(lambda c: c.data == "search")
async def process_search(callback_query: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    composition = state_data.get("composition", {})

    # Find matching steels
    matches = find_matching_steels(composition)

    if matches:
        response = "Найдены подходящие марки стали:\n\n"
        for steel_grade, specification, *_ in matches:
            response += f"Марка стали: {steel_grade}\nСпецификация: {specification}\n\n"
        await callback_query.message.answer(response)
        await state.clear()
    else:
        # Ask if user wants to find the closest steel
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data="find_closest"),
                InlineKeyboardButton(text="Нет", callback_data="cancel_search")
            ]
        ])
        await callback_query.message.answer(
            "Для данного состава не найдено подходящих марок стали.\n"
            "Хотите найти наиболее близкую марку стали?",
            reply_markup=keyboard
        )
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "find_closest")
async def process_find_closest(callback_query: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    composition = state_data.get("composition", {})

    # Find the closest steel
    closest = find_closest_steel(composition)

    if closest:
        steel_grade, specification, db_composition = closest
        response = "Найдена наиболее близкая марка стали:\n\n"
        response += f"Марка стали: {steel_grade}\n"
        response += f"Спецификация: {specification}\n\n"
        response += "Средний состав марки стали:\n"
        for element, value in db_composition.items():
            response += f"{element}: {value:.3f}%\n"
    else:
        response = "Не удалось найти подходящую марку стали."

    await callback_query.message.answer(response)
    await state.clear()
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "cancel_search")
async def process_cancel_search(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Поиск отменен.")
    await state.clear()
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "new_search")
async def process_new_search(callback_query: CallbackQuery, state: FSMContext):
    # Reset composition to all zeros
    composition = {element: 0.0 for element in ELEMENTS}
    await state.update_data(composition=composition)

    # Create the message with reset values
    message_text = "Химический состав стали (в %):\n\n"
    message_text += "Нажмите на элемент, чтобы изменить его значение\n"

    # Create keyboard with reset values
    keyboard = create_composition_keyboard(composition)

    await state.set_state(SteelComposition.waiting_for_composition)
    await callback_query.message.answer(message_text, reply_markup=keyboard)
    await callback_query.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())