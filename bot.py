from config import login, password, token
import telebot
from instabot import Bot
from loguru import logger


logger.add('logs.log', format='{time} {level} {message}', rotation='10 MB')
error_flag = False  # Детектор ошибок

if __name__ == '__main__':
    # Авторизация в инсте
    try:
        bot_inst = Bot()
        bot_inst.login(username=login, password=password, use_cookie=True)
    except Exception:
        error_flag = True
        logger.error('Ошибка входа в инстаграм')

    bot_tg = telebot.TeleBot(token)


    @bot_tg.message_handler(content_types=['text'])
    def get_text_messages(message):
        """Обработка сообщений тг"""
        if message.text == "/start":
            if not error_flag:
                bot_tg.send_message(message.from_user.id,
                                    'Напиши имя пользователя, о котором ты хочешь узнать информацию\U0001F440')
                bot_tg.register_next_step_handler(message, instabot)
            else:
                bot_tg.send_message(message.from_user.id, 'Приносим извинения, бот временно не работает\U0001F614')
        else:
            bot_tg.send_message(message.from_user.id, '\U0001F4CDСписок команд:\n\n/start - узнать невзаимных')


    def instabot(message) -> None:
        """Поиск невзаимных подписчиков в инсте"""
        bot_tg.send_message(message.from_user.id, 'Идет сбор информации \U0001F30D')
        user = message.text
        followers = set()
        following = set()
        try:
            followers.update(set(bot_inst.get_user_followers(user)))
            following.update(set(bot_inst.get_user_following(user)))

            # Для точности результата необходимо пройтись ещё несколько раз
            for i in range(4):
                followers = followers.union(set(bot_inst.get_user_followers(user)))
                following = following.union(set(bot_inst.get_user_following(user)))

            finish = list(following.difference(followers))

            count = len(finish)
            string_answer = f'Всего {count} не подписанных на вас взаимно пользователей.\U0001F310\n' \
                            f'Подготавливаем список\U0001F504'
            bot_tg.send_message(message.from_user.id, string_answer)
            string_answer = ''
            for i in range(count):
                string_answer += str(i + 1) + '. https://www.instagram.com/' +\
                                 str(bot_inst.get_username_from_user_id(finish[i])) + '\n'
            bot_tg.send_message(message.from_user.id, string_answer)
        except Exception:
            bot_tg.send_message(message.from_user.id,
                                'Произошла ошибка\U0001F624\n Возможно этот аккаунт закрыт\U0001F614')

    bot_tg.polling(none_stop=True)
