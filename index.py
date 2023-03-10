from langchain.llms import OpenAI
from langchain import PromptTemplate, LLMChain
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
import os
import logging
from dotenv import load_dotenv
load_dotenv()

davinci = OpenAI(model_name='text-davinci-003')

# build prompt template for simple question-answering
template = """Question: {question}

Answer: """
prompt = PromptTemplate(template=template, input_variables=["question"])

llm_chain = LLMChain(
    prompt=prompt,
    llm=davinci
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    answer = llm_chain.run(question)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(
        os.environ["TG_ACCESS_TOKEN"]).build()

    question_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), question)
    start_handler = CommandHandler('start', start)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(question_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
