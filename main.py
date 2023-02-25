import telebot
import medicine
import openai
import re
import parser
import codecs
import uuid
import os
import speech_recognition as sr
import soundfile as sf


teletoken = "6049181079:AAGJXq0VmX5M05d3DAatiS2_weWEEOz59Us"
bot = telebot.TeleBot(teletoken, parse_mode=None)
GPT_token = "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"
model = "text-davinci-003"
openai.api_key = GPT_token
language = 'ru_RU'
r = sr.Recognizer()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет друг\nНапиши, пожалуйста, свои симптомы и я подскажу что и где тебе "
                                      "нужно купить, чтобы вылечиться в кратчайшие сроки")


@bot.message_handler()
def send_message(message):
    print(message.text)
    prompt = message.text + ". Напиши поисковый запрос в интернет магазин, который принимает только названия. И " \
                            "каждое лекарство по отдельности впиши в квадратные скобки."
    send(prompt, message)


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    filename = str(uuid.uuid4())
    file_name_full = "./voice/" + filename + ".ogg"
    file_name_full_converted = "./ready/" + filename + ".wav"
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open(file_name_full, 'wb') as new_file:
        new_file.write(downloaded_file)
    print(file_name_full)
    data, samplerate = sf.read(file_name_full)
    sf.write(file_name_full_converted, data, samplerate)
    text = audio_to_text(file_name_full_converted)
    os.remove(file_name_full)
    os.remove(file_name_full_converted)
    send(text + ". Напиши поисковый запрос в интернет магазин, который принимает только названия. И каждое лекарство "
                "по отдельности впиши в квадратные скобки.", message)


def audio_to_text(audio_file):
    # создаем объект распознавания речи
    r = sr.Recognizer()

    # открываем аудиофайл
    with sr.AudioFile(audio_file) as source:
        audio_data = r.record(source)

    # используем распознавание речи Google для преобразования аудио в текст
    text = r.recognize_google(audio_data, language="ru-RU")
    return text

def send(prompt, message):
    response = openai.Completion.create(engine=model, prompt=prompt, max_tokens=250)
    text = response
    pattern = r"\[(.*?)\]"
    result = re.findall(pattern, str(text))
    mas = []
    for q in result:
        mas += (str(q).replace('"', ",").replace(";", ",").replace(".", ",").split(sep=","))
    print(response.choices[0].text)
    message_text = ""
    print(mas)
    for key in mas:
        keyw = codecs.decode(key, 'unicode_escape')
        print(keyw)
        medicine_res = parser.Parser("http://e-apteka.md").parse(keyw)
        print(medicine_res)
        if medicine_res == []:
            continue
        message_text += "\nВы можете купить <b>" + keyw + "</b>\n"
        for i in medicine_res:
            message_text += ('Название: <a href="' + i['link'] + '">' + i['name'] + "</a>\n")
            message_text += ("Цена: " + i['price'] + "\n\n")
    if message_text == "":
        message_text = "Товарв не найдено"
    bot.send_message(message.chat.id, message_text, parse_mode="HTML")

bot.infinity_polling()
