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
    waiting_for_element = State()
    waiting_for_value = State()
    waiting_for_confirmation = State()

# Database connection
def get_db_connection():
    return sqlite3.connect('steel_database.db')

# Function to find matching steel grades
def find_matching_steels(composition: Dict[str, float]) -> List[tuple]:
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT steel_grade, specification
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
        Zr_min <= ? AND Zr_max >= ?
    """

    params = []
    for element in ['C', 'Si', 'Mn', 'S', 'P', 'Cr', 'Ni', 'Cu', 'Mo', 'V', 'Nb', 'Ti', 'N', 'W', 'B', 'Zr']:
        value = composition.get(element, 0)
        params.extend([value, value])

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

# List of elements to ask for
ELEMENTS = ['C', 'Si', 'Mn', 'S', 'P', 'Cr', 'Ni', 'Cu', 'Mo', 'V', 'Nb', 'Ti', 'N', 'W', 'B', 'Zr']

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать в бот для поиска марок стали! 🏭\n\n"
        "Я помогу вам найти марки стали на основе их химического состава.\n"
        "Используйте команду /find, чтобы начать поиск."
    )

@dp.message(Command("find"))
async def cmd_find(message: Message, state: FSMContext):
    # Initialize the composition dictionary
    await state.update_data(composition={}, current_element_index=0)

    # Get the first element
    element = ELEMENTS[0]

    # Create confirmation buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_{element}"),
            InlineKeyboardButton(text="Исправить", callback_data=f"edit_{element}")
        ]
    ])

    await state.set_state(SteelComposition.waiting_for_value)
    await message.answer(f"Введите содержание {element}:", reply_markup=keyboard)

@dp.message(SteelComposition.waiting_for_value)
async def process_element_value(message: Message, state: FSMContext):
    try:
        # Get the current state data
        state_data = await state.get_data()
        current_index = state_data.get("current_element_index", 0)
        composition = state_data.get("composition", {})

        # Get the current element
        current_element = ELEMENTS[current_index]

        # Parse the value
        value = float(message.text)

        # Update the composition
        composition[current_element] = value
        await state.update_data(composition=composition)

        # Create confirmation buttons
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_{current_element}"),
                InlineKeyboardButton(text="Исправить", callback_data=f"edit_{current_element}")
            ]
        ])

        await state.set_state(SteelComposition.waiting_for_confirmation)
        await message.answer(f"Вы ввели {current_element}: {value}. Подтвердите или исправьте:", reply_markup=keyboard)

    except ValueError:
        await message.answer(f"Пожалуйста, введите числовое значение для {ELEMENTS[current_index]}.")

@dp.callback_query(lambda c: c.data.startswith("confirm_"))
async def process_confirmation(callback_query: CallbackQuery, state: FSMContext):
    # Get the current state data
    state_data = await state.get_data()
    current_index = state_data.get("current_element_index", 0)
    composition = state_data.get("composition", {})

    # Move to the next element
    current_index += 1

    # Check if we've processed all elements
    if current_index >= len(ELEMENTS):
        # Find matching steels
        matches = find_matching_steels(composition)

        if matches:
            response = "Найдены подходящие марки стали:\n\n"
            for steel_grade, specification in matches:
                response += f"Марка стали: {steel_grade}\nСпецификация: {specification}\n\n"
        else:
            response = "Для данного состава не найдено подходящих марок стали."

        await callback_query.message.answer(response)
        await state.clear()
        await callback_query.answer()
        return

    # Update the state with the new index
    await state.update_data(current_element_index=current_index)

    # Get the next element
    next_element = ELEMENTS[current_index]

    # Create confirmation buttons for the next element
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_{next_element}"),
            InlineKeyboardButton(text="Исправить", callback_data=f"edit_{next_element}")
        ]
    ])

    await state.set_state(SteelComposition.waiting_for_value)
    await callback_query.message.answer(f"Введите содержание {next_element}:", reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("edit_"))
async def process_edit(callback_query: CallbackQuery, state: FSMContext):
    # Get the current state data
    state_data = await state.get_data()
    current_index = state_data.get("current_element_index", 0)

    # Get the current element
    current_element = ELEMENTS[current_index]

    # Create confirmation buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_{current_element}"),
            InlineKeyboardButton(text="Исправить", callback_data=f"edit_{current_element}")
        ]
    ])

    await state.set_state(SteelComposition.waiting_for_value)
    await callback_query.message.answer(f"Введите содержание {current_element}:", reply_markup=keyboard)
    await callback_query.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())