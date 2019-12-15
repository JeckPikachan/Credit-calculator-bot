from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import matplotlib.pyplot as plt

import logging
from enum import Enum

from config import TG_TOKEN
import financial


last_command = {}


class Commands(Enum):
    NONE = 0,
    CREDIT = 1,
    DEPOSIT = 2


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def bot_help(update, context):
    pass


def deposit(update: Update, context: CallbackContext):
    last_command[update.effective_chat.id] = Commands.DEPOSIT
    context.bot.send_message(chat_id=update.effective_chat.id
                             , text="please type [initial payment sum] [annual interest rate] [period in months] to get info about your deposit")


def credit(update: Update, context: CallbackContext):
    last_command[update.effective_chat.id] = Commands.CREDIT
    context.bot.send_message(chat_id=update.effective_chat.id
                             , text="please type [payment sum] [annual interest rate] [period in months] to get info about your credit")


def _get_markdown_credit(mpi: financial.MainPaymentInfo, history):
    res = f"Monthly annuity payment: *{mpi.monthly_annuity_payment:.2f}*\n"
    res += f"Credit body: *{mpi.credit_body:.2f}*\n"
    res += f"Total payment: *{mpi.total_payment_sum:.2f}*\n"
    res += f"Overpayment: *{mpi.overpayment:.2f}*\n"
    res += f"Effective interest rate: *{mpi.effective_interest_rate:.2f}%*\n\n"

    res += "``` Months |    Monthly payment    |        Percent       |         Body         |       Left debt      |\n"
    res +=     "------ | --------------------- | -------------------- | -------------------- | -------------------- |\n"

    for i, data, in enumerate(history):
        res += f"{i + 1:>6} | {mpi.monthly_annuity_payment:>21.2f} | {history[i].percent:>20.2f} | {history[i].body:>20.2f} | {history[i].left:>20.2f} |\n"

    res += "```"
    return res


def _get_credit_graphic(chat_id, history):
    x = [i + 1 for i in range(len(history))]
    body = [i.body for i in history]
    percent = [i.percent for i in history]
    left = [i.left for i in history]

    fig, axs = plt.subplots(2)
    axs[0].plot(x, body)
    axs[0].plot(x, percent)
    axs[0].set(title="Monthly percent and body payment")

    axs[1].plot(x, left)
    axs[1].set(title="Monthly left debt")

    fig.subplots_adjust(hspace=0.3)
    name = str(chat_id) + ".png"
    fig.savefig(name)

    return name


def _get_deposit_graphic(chat_id, history, history_with_cap):
    x = [i + 1 for i in range(len(history))]

    fig, axs = plt.subplots(1)
    axs.plot(x, history)
    axs.plot(x, history_with_cap)
    axs.set(title="balance without capitalization and with monthly capitalization")
    name = str(chat_id) + "dep.png"
    fig.savefig(name)

    return name


def _get_markdown_deposit(revenue, revenue_with_cap, history, history_with_cap):
    res = f"Revenue without capitalization: *{revenue:.2f}*\n"
    res += f"Revenue with monthly capitalization: *{revenue_with_cap:.2f}*\n\n"

    res += "``` Months | Without capitalization | With monthly capitalization \n"
    res +=     "------ | ---------------------- | --------------------------- \n"

    for i, data in enumerate(zip(history, history_with_cap)):
        res += f"{i + 1:>6} | {data[0]:>22.2f} | {data[1]:>27.2f} \n"

    res += "```"

    return res


def _parse_args(message):
    splitted = message.split(" ")
    if len(splitted) != 3:
        raise ValueError("You should provide exactly 3 arguments")

    try:
        splitted[0] = float(splitted[0])
        splitted[1] = float(splitted[1])
        splitted[2] = int(splitted[2])
    except ValueError as e:
        raise ValueError("All arguments should be numbers")

    return splitted


def message(update: Update, context: CallbackContext):
    if update.effective_chat.id in last_command:
        try:
            if last_command[update.effective_chat.id] == Commands.CREDIT:
                splitted = _parse_args(update.message.text)

                mpi = financial.get_main_payment_info(splitted[0], splitted[1], splitted[2])
                history = financial.get_payment_history(splitted[0], splitted[1], splitted[2])

                context.bot.send_message(chat_id=update.effective_chat.id, text=_get_markdown_credit(mpi, history)
                                         , parse_mode="Markdown")

                img = _get_credit_graphic(update.effective_chat.id, history)
                with open(img, 'rb') as f:
                    context.bot.send_photo(chat_id=update.effective_chat.id, photo=f)

            elif last_command[update.effective_chat.id] == Commands.DEPOSIT:
                splitted = _parse_args(update.message.text)

                revenue, revenue_with_cap = financial.get_deposit_revenue(splitted[0], splitted[1], splitted[2])
                history, history_with_cap = financial.get_deposit_history(splitted[0], splitted[1], splitted[2])

                context.bot.send_message(chat_id=update.effective_chat.id
                                         , text=_get_markdown_deposit(revenue, revenue_with_cap, history, history_with_cap)
                                         , parse_mode="Markdown")

                img = _get_deposit_graphic(update.effective_chat.id, history, history_with_cap)
                with open(img, 'rb') as f:
                    context.bot.send_photo(chat_id=update.effective_chat.id, photo=f)

        except ValueError as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text=str(e))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please choose command first")


def main():
    updater = Updater(token=TG_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    help_handler = CommandHandler('help', bot_help)
    dispatcher.add_handler(help_handler)

    credit_handler = CommandHandler('credit', credit)
    dispatcher.add_handler(credit_handler)

    deposit_handler = CommandHandler('deposit', deposit)
    dispatcher.add_handler(deposit_handler)

    message_handler = MessageHandler(Filters.regex(r"\d* \d* \d*"), message)
    dispatcher.add_handler(message_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
