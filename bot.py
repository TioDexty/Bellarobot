import telebot
import model
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove

token = "1275482560:AAFeRkU3jh3mdfWxbhzJs-7VaYZuKhpqXy8"
bot = telebot.TeleBot(token)

post_dict = {}  # saves posts data while user's working on it
storage_channel_id = "@DextyOficial"  # channel's id to send final results to


def main_menu_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Faze Uma Nova Postagem", callback_data="create_post"))
    return markup


def post_markup(message):
    post = post_dict[message.chat.id]
    word = post.words[-1]
    definition_number = len(word.definitions) + 1
    markup = InlineKeyboardMarkup()
    cancel_button = InlineKeyboardButton("Cancelar ❎", callback_data="cancel")
    finish_button = InlineKeyboardButton("Finaliza ☑️", callback_data="finish")

    markup.row(cancel_button, finish_button)

    return markup


def skip_markup():
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(KeyboardButton('@DextyOficialBot'))
    return markup

def send_to_storage_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Enviar [ ✔️ ]", callback_data="send_to_storage"),
               InlineKeyboardButton("Editar [ 🖍️ ]", callback_data="edit_before_sending"),
               InlineKeyboardButton("Cancelar [ ❎ ]", callback_data="cancel_sending_to_storage"),)
    return markup


@bot.message_handler(commands=['start'])
def process_start(message):
    bot.send_message(message.chat.id, "CRIE UMA NOVA POSTAGEM AQUI ✅\n\nNAO POSTE COISAS PROIBIDAS COMO PORNOGRAFIA ❌ \n\nVOCE PODE SER BANIDO DO BOT 😱",
                     reply_markup=main_menu_markup())


@bot.callback_query_handler(func=lambda call: True)
def test_callback(call):
    if call.data == "create_post":
        bot.answer_callback_query(call.id, "Criando postagem!")
        post = model.Post()
        post_dict[call.message.chat.id] = post
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Envie sua Postagem🖍️.")
                                    
        bot.register_next_step_handler(msg, process_word_name)
    if call.data == "cancel":
        bot.answer_callback_query(call.id, "Cancelando a criação da postagem!")
        post_dict.pop(call.message.chat.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="CRIE UMA NOVA POSTAGEM AQUI ✅\n\nNAO POSTE COISAS PROIBIDAS COMO PORNOGRAFIA ❌ \n\nVOCE PODE SER BANIDO DO BOT 😱", reply_markup=main_menu_markup())
    if call.data == "finish":
        bot.answer_callback_query(call.id, "Esta é a sua postagem!")
        post = post_dict[call.message.chat.id]
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=post.print_post(), parse_mode="Markdown")
        links = post.print_links()
        if links:
            bot.send_message(call.message.chat.id, links, parse_mode="Markdown")
        bot.send_message(call.message.chat.id, "Você pode enviar essas postagens para o armazenamento ou editá-las manualmente e depois "
                                               "Envie isto. Pressione o botão 'Cancelar' para não fazer isso.",
                         reply_markup=send_to_storage_markup())
    if call.data == "send_to_storage":
        bot.answer_callback_query(call.id, "Enviando pro Canal✔️!")
        post = post_dict[call.message.chat.id]
        bot.send_message(storage_channel_id, post.print_post(), parse_mode="Markdown")
        links = post.print_links()
        if links:
            bot.send_message(storage_channel_id, links, parse_mode="Markdown")
        post_dict.pop(call.message.chat.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="CRIE UMA NOVA POSTAGEM AQUI ✅\n\nNAO POSTE COISAS PROIBIDAS COMO PORNOGRAFIA ❌ \n\nVOCE PODE SER BANIDO DO BOT 😱", reply_markup=main_menu_markup())
    if call.data == "edit_before_sending":
        bot.answer_callback_query(call.id, "Editando!")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Envie uma postagem editada manualmente aqui.")
        post = post_dict[call.message.chat.id]
        msg = bot.send_message(call.message.chat.id, post.print_post())
        bot.register_next_step_handler(msg, process_edited_post)
    if call.data == "cancel_sending_to_storage":
        post_dict.pop(call.message.chat.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="CRIE UMA NOVA POSTAGEM AQUI ✅\n\nNAO POSTE COISAS PROIBIDAS COMO PORNOGRAFIA ❌ \n\nVOCE PODE SER BANIDO DO BOT 😱", reply_markup=main_menu_markup())


def process_word_name(message):
    word_name = message.text
    word_name = word_name.capitalize()
    post = post_dict[message.chat.id]
    new_word = model.Word(word_name)
    post.words.append(new_word)
    post_dict[message.chat.id] = post
    msg = bot.send_message(message.chat.id, 'Caso Nao Envie seu Usuário A Postagem sera Nomeada Como "@DextyOficialBot"',
                           reply_markup=skip_markup())
    bot.register_next_step_handler(msg, process_part_of_speech)


def process_phonetic_transcription(message):
    if message.text != '@DextyOficialBot':
        phonetic_transcription = message.text
        characters_to_replace = ['/', '\\', '[', ']']
        for char in characters_to_replace:
            phonetic_transcription = phonetic_transcription.replace(char, '')
        post = post_dict[message.chat.id]
        word = post.words[-1]
        word.phoneticTranscription = phonetic_transcription
        post_dict[message.chat.id] = post

    msg = bot.send_message(message.chat.id, "Escolha parte do discurso entre as opções abaixo.",
                           reply_markup=parts_of_speech_markup())
    bot.register_next_step_handler(msg, send_to_storage_markup)


def process_part_of_speech(message):
    part_of_speech = message.text
    post = post_dict[message.chat.id]
    word = post.words[-1]
    word.partOfSpeech = part_of_speech
    post_dict[message.chat.id] = post
    bot.send_message(message.chat.id, post.print_post(), reply_markup=post_markup(message), parse_mode="Markdown")

def process_edited_post(message):
    post = post_dict[message.chat.id]
    post_edited = message.text
    bot.send_message(storage_channel_id, post_edited, parse_mode="Markdown")
    links = post.print_links()
    if links:
        bot.send_message(storage_channel_id, links, parse_mode="Markdown")
    post_dict.pop(message.chat.id)
    bot.send_message(message.chat.id, "CRIE UMA NOVA POSTAGEM AQUI ✅\n\nNAO POSTE COISAS PROIBIDAS COMO PORNOGRAFIA ❌ \n\nVOCE PODE SER BANIDO DO BOT 😱 ", reply_markup=main_menu_markup())


if __name__ == "__main__":
    bot.polling(none_stop=True)
