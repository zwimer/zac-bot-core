def invoke(update, context, log_file):
    chat_id = update.message.chat_id
    with open(log_file, 'rb') as f:
        context.bot.send_document(chat_id=chat_id, document=f)
