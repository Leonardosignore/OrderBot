import asyncio
import os
from aiogram.types import CallbackQuery
from dotenv import load_dotenv
from database import get_categorie, init_db, seed_prodotti, get_prodotti
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.filters import Command
from database import crea_ordine
from database import get_ordini_pending
from database import conferma_ordine, scala_quantita
from database import annulla_ordine
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("leo")
BOT_TOKEN = os.getenv("BOT_TOKEN")
VENDITORE_ID = int(os.getenv("VENDITORE_ID"))

ORDINI_IN_CORSO = {}
CATEGORIE = ["40K", "60K"]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def invia_lista_prodotti(target):
    prodotti = get_prodotti()

    if not prodotti:
        await target.answer("❌ Nessun prodotto disponibile.")
        return

    testo = "📦 Prodotti disponibili:\n\n"
    for nome, quantita, categoria, prezzo in prodotti:
        testo += f"- {nome} {categoria}: {prezzo}€\n"

    await target.answer(testo)

@dp.message(CommandStart())
async def start(message: Message):
    
    if message.from_user.id == VENDITORE_ID:
        await message.answer(
                        "👋 Benvenuto, venditore.\n\n"
            "Comandi disponibili:\n"
            "/prodotti → visualizza le disponibilità\n"
            "/ordini → lista ordini in attesa\n"
            "/conferma ID_ORDINE → conferma un ordine\n"
            "/annulla ID_ORDINE → annulla un ordine\n\n"
            "Usa questi comandi per gestire le vendite."
        )
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📦 Consulta prodotti", callback_data="prodotti")
        ],
        [
            InlineKeyboardButton(text="🛒 Effettua un ordine", callback_data="ordina")
        ]
    ])
    await message.answer(
        "👋 Benvenuto!\n\n"
        "Con questo bot puoi consultare i prodotti disponibili e fare un ordine.\n\n"
        "Usa i pulsanti qui sotto per iniziare 👇",
        reply_markup=keyboard
        )

@dp.message(Command("prodotti"))
async def lista_prodotti(message: Message):
    logger.info("Handler /prodotti chiamato")
    await invia_lista_prodotti(message)

@dp.callback_query(lambda c: c.data in ["ordina", "prodotti"])
async def scegli_categoria(callback: CallbackQuery):
    await callback.answer()
    
    CATEGORIE = get_categorie()
    
    logger.info(CATEGORIE)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cat, callback_data=f"categoria:{cat}")]
            for cat in CATEGORIE
        ]
    )

    action = "ordinare" if callback.data == "ordina" else "consultare"
    await callback.message.answer(
        f"Seleziona la categoria di prodotti da {action}:",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("categoria:"))
async def mostra_prodotti_categoria(callback: CallbackQuery):
    logger.info("Handler /categoria ")
    await callback.answer()

    categoria = callback.data.split(":")[1]

    ORDINI_IN_CORSO[callback.from_user.id] = {
        "categoria": categoria
    }

    prodotti = get_prodotti(categoria)  # assume get_prodotti accetta categoria come argomento

    if not prodotti:
        await callback.message.answer("❌ Nessun prodotto disponibile in questa categoria.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{nome} ({quantita})", callback_data=f"ordina_prodotto:{nome}")]
            for nome, quantita, *_ in prodotti
        ]
    )

    await callback.message.answer(
        f"Prodotti disponibili nella categoria {categoria}:",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("ordina_prodotto:"))
async def scegli_prodotto(callback: CallbackQuery):
    logger.info("Handler /ordina_prodotto: ")
    await callback.answer()

    nome_prodotto = callback.data.split(":")[1]

    ORDINI_IN_CORSO[callback.from_user.id].update({
        "prodotto": nome_prodotto,
        "fase": "quantita"
    })

    await callback.message.answer(
        f"📦 Hai scelto: *{nome_prodotto}*\n\n"
        "✏️ Ora scrivi la quantità desiderata:",
        parse_mode="Markdown"
    )

@dp.message(Command("ordina"))
async def ordina(message: Message):
    logger.info("Handler /ordina chiamato")
    prodotti = get_prodotti()

    if not prodotti:
        await message.answer("❌ Nessun prodotto disponibile.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{nome} ({quantita})",
                callback_data=f"ordina_prodotto:{nome}"
            )]
            for nome, quantita in prodotti
        ]
    )

    await message.answer(
        "🛒 Scegli il prodotto da ordinare:",
        reply_markup=keyboard
    ) 

@dp.message(Command("ordini"))
async def lista_ordini(message: Message):
    logger.info("Handler /ordini ")
    if message.from_user.id != VENDITORE_ID:
        logger.info("non sono il venditore", message.from_user.id, VENDITORE_ID)
        return

    ordini = get_ordini_pending()

    if not ordini:
        await message.answer("📭 Nessun ordine in attesa.")
        return

    testo = "📋 Ordini in attesa:\n\n"
    for oid, user_id, nome_cliente, prodotto, quantita in ordini:
        testo += (
            f"ID: {oid}\n"
            f"Prodotto: {prodotto}\n"
            f"Quantità: {quantita}\n"
            f"Cliente: {nome_cliente}\n\n"
        )

    await message.answer(testo)

@dp.message(Command("annulla"))
async def annulla(message: Message):
    if message.from_user.id != VENDITORE_ID:
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Usa: /annulla ID_ORDINE")
        return

    ordine_id = int(parts[1])
    annulla_ordine(ordine_id)

    await message.answer(f"❌ Ordine {ordine_id} annullato.")

@dp.message(Command("conferma"))
async def conferma(message: Message):
    if message.from_user.id != VENDITORE_ID:
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Usa: /conferma ID_ORDINE")
        return

    ordine_id = int(parts[1])

    ordini = get_ordini_pending()
    ordine = next((o for o in ordini if o[0] == ordine_id), None)

    if not ordine:
        await message.answer("❌ Ordine non trovato o già gestito.")
        return

    _, user_id, nome_cliente, prodotto, quantita = ordine

    scala_quantita(prodotto, quantita)
    conferma_ordine(ordine_id)

    await message.answer(f"✅ Ordine {ordine_id} confermato.")
    await bot.send_message(user_id, f"✅ Il tuo ordine {ordine_id} è stato confermato.")

@dp.message(Command("id"))
async def get_id(message: Message):
    await message.answer(f"Il tuo ID è: {message.from_user.id}")



@dp.message()
async def ricevi_quantita(message: Message):
    user_id = message.from_user.id

    if user_id not in ORDINI_IN_CORSO:
        return

    stato = ORDINI_IN_CORSO[user_id]

    if stato["fase"] != "quantita":
        return

    if not message.text.isdigit():
        await message.answer("❌ Inserisci solo un numero.")
        return

    quantita = int(message.text)
    if quantita <= 0:
        await message.answer("❌ Quantità non valida.")
        return

    nome_prodotto = stato["prodotto"]

    categoria = stato["categoria"]
    products = {nome: quantita for nome, quantita, *_ in get_prodotti(categoria)}
    if quantita > products.get(nome_prodotto, 0):
        await message.answer("❌ Quantità non disponibile.")
        return

    # nome cliente
    user = message.from_user
    nome_cliente = (
        f"@{user.username}"
        if user.username
        else f"{user.first_name} {user.last_name or ''}".strip()
    )

    ordine_id = crea_ordine(
        user_id,
        nome_cliente,
        nome_prodotto,
        quantita
    )

    del ORDINI_IN_CORSO[user_id]

    await message.answer(
        f"📝 Ordine registrato!\n\n"
        f"ID: {ordine_id}\n"
        f"Prodotto: {nome_prodotto}\n"
        f"Quantità: {quantita}"
    )

    await bot.send_message(
        VENDITORE_ID,
        f"📦 Nuovo ordine\n\n"
        f"ID: {ordine_id}\n"
        f"Cliente: {nome_cliente}\n"
        f"Prodotto: {nome_prodotto}\n"
        f"Quantità: {quantita}"
    )

async def main():
    init_db()
    seed_prodotti()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())