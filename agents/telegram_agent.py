import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from agents.proposal import Proposal
from database import queries
from utils.logger import get_logger

logger = get_logger(__name__)

ACTIONABLE = {"pausar", "escalar", "redistribuir"}
ACTION_EMOJI = {"pausar": "⏸️", "escalar": "📈", "redistribuir": "🔁", "mantener": "✅"}


def build_summary_message(account_name: str, proposals: list[Proposal]) -> str:
    lines = [f"📊 Resumen semanal — {account_name}\n"]
    if not proposals:
        lines.append("Sin propuestas esta semana. Todas las campañas están dentro de los parámetros esperados.")
        return "\n".join(lines)

    for p in proposals:
        emoji = ACTION_EMOJI.get(p.action, "•")
        lines.append(f"{emoji} {p.campaign_name} → {p.action}\n   {p.reason}")
    return "\n\n".join(lines)


async def send_proposals(bot_token: str, chat_id: str, proposals: list[Proposal]) -> None:
    """Loguea cada propuesta accionable en la base y la manda por Telegram con
    botones de aprobación. Las propuestas 'mantener' son informativas, no requieren aprobación."""
    bot = Bot(token=bot_token)
    actionable = [p for p in proposals if p.action in ACTIONABLE]

    if not actionable:
        await bot.send_message(chat_id=chat_id, text="✅ Sin cambios propuestos esta semana.")
        return

    for p in actionable:
        decision_id = queries.log_decision(p)
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Aprobar", callback_data=f"{decision_id}:approve"),
            InlineKeyboardButton("❌ Rechazar", callback_data=f"{decision_id}:reject"),
        ]])
        text = f"{p.campaign_name}\nAcción propuesta: {p.action}\n{p.reason}"
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


async def _on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    decision_id_str, action = query.data.split(":")
    status = "approved" if action == "approve" else "rejected"
    queries.update_decision_status(int(decision_id_str), status)
    await query.answer()
    label = "✅ Aprobado" if status == "approved" else "❌ Rechazado"
    await query.edit_message_text(text=f"{query.message.text}\n\n{label}")


def run_approval_listener() -> None:
    """Proceso de larga duración separado del cron semanal: GitHub Actions solo
    manda las propuestas y termina, así que los clicks de aprobación necesitan
    este listener corriendo en algún lugar (server propio, Railway, etc)."""
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = Application.builder().token(token).build()
    app.add_handler(CallbackQueryHandler(_on_callback))
    logger.info("Escuchando aprobaciones de Telegram (Ctrl+C para detener)...")
    app.run_polling()


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    run_approval_listener()
