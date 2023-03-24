from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.chat_models import PromptLayerChatOpenAI
from langchain.chains import LLMChain, ConversationChain
from langchain.memory import ConversationBufferMemory
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
import os
import logging
from dotenv import load_dotenv
load_dotenv()


llm = PromptLayerChatOpenAI(model_name="gpt-4", pl_tags=["langchain"], temperature=0)


prompt = ChatPromptTemplate.from_messages(
    [SystemMessagePromptTemplate.from_template("The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know."),
     MessagesPlaceholder(variable_name="history"),
     HumanMessagePromptTemplate.from_template("{input}")
     ])

memory = ConversationBufferMemory(return_messages=True)

conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    answer = conversation.predict(input=question)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(
        os.environ["TG_ACCESS_TOKEN"]).build()

    question_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND), question)
    start_handler = CommandHandler('start', start)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(question_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
