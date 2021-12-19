import logging
import random
import sqlite3
# import asyncio
from time import time
from app.app import config


class Markov:
    """
    Class for Markov chain logic
        matrix - dict with chain statistics
        windows - list of avialable window sizes for chain
        last_text - last characters of last added text
        rand_coeff - chance of random (non-statistical) elongation (in promille)
    """
    def __init__(self, order: int = None, rand_coeff: int = 10):
        """
        :param order: size of chain's window
        :param rand_coeff: coefficient of random
        """
        self.matrix = {}
        if order is None:
            self.windows = [9, 6, 3, 1]
        else:
            self.windows = [order, 9, 6, 3, 1]
        self.N = self.windows[0]
        self.last_text = ' ' * self.N
        # last_text good for answer generations or if model was learned on separate sentences
        self.rand_coeff = rand_coeff

    def _make_pairs(self, text: str, last_text_enabled: bool) -> tuple[str, str]:
        """
        Generator function; Makes "key sequence - next character" pairs
        :param text: text to analyze
        :param last_text_enabled: enable last_text parameter
        :return: tuple (key_seq, next_char)
        """
        if last_text_enabled is True:
            for n in self.windows:
                if len(text) >= n:
                    yield '_START', text[:n]
                    text = (self.last_text + ' ' + text).strip()
                    self.last_text = text[-n:]
                    break
                else:
                    continue
        else:
            for n in self.windows:
                if len(text) >= n:
                    yield '_START', text[:n]
                    break
                else:
                    continue
        for n in self.windows:
            if len(text) >= n:
                for i in range(len(text)):
                    if i < (len(text) - n):
                        key_seq, next_char = text[i: i + n], text[i + n]
                        yield key_seq, next_char
                    else:
                        key_seq, next_char = text[i: i + n], None
                        yield key_seq, next_char
                        break
            else:
                continue

    def parse_and_add(self, text: str, last_text_enabled: bool = True):
        """
        Makes pairs from text and adds them to statistic matrix
        :param text: text to analyze
        :param last_text_enabled: enable last_text in model
        """
        for i in self._make_pairs(text, last_text_enabled):
            try:
                self.matrix[i[0]][i[1]] += 1
            except KeyError:
                try:
                    self.matrix[i[0]][i[1]] = 1
                except KeyError:
                    self.matrix[i[0]] = {i[1]: 1}

    def _get_primer(self) -> str:
        """
        Returns first characters of text from matrix
        :return: string
        """
        try:
            primer = random. \
                choices(list(self.matrix['_START'].keys()), weights=list(self.matrix['_START'].values()))[0]
        except KeyError:
            primer = 'Недостаточно данных для генерациии сообщений.\
                        \nБот учится на ваших сообщениях, напишите что-нибудь!'
        return primer

    def _elongate(self, primer: str, ignore_none=False, strict=False) -> tuple[str, bool]:
        """
        Elongates the given primer by 1 char
        :param primer: string to elongate
        :param ignore_none: if True - elongate, ignoring text endings
        :param strict: if True - elongate even if primer can't be found in matrix
        :return: tuple (elongated primer, is_end_of_text)
        """
        for n in self.windows:
            try:
                if random.randint(0, 1000) > self.rand_coeff:
                    next_char = random.choices(list(self.matrix[primer[-n:]].keys()),
                                               list(self.matrix[primer[-n:]].values()))[0]
                else:
                    next_char = random.choice(list(self.matrix[random.choice(list(self.matrix.keys()))].keys()))

                if next_char is None:
                    if ignore_none is False:
                        return primer, True
                    else:
                        if len(self.matrix[primer[-n:]]) > 1:
                            temp = self.matrix[primer[-n:]].copy()
                            temp.pop(None)
                            next_char = random.choices(list(temp.keys()),
                                                       list(temp.values()))[0]
                            del temp
                            return ''.join([primer, next_char]), False
                        else:
                            continue
                else:
                    return ''.join([primer, next_char]), False
            except KeyError:
                continue
        else:
            if strict is True:
                return ''.join([primer, self._get_primer()]), False
            else:
                return primer, True

    def generate_l(self, string: str = None, lengthmin: int = 1, lengthmax: int = 500) -> str:
        """
        Generates text from primer string (if given) within specified length borders
        Sometimes text may be slightly longer than lengthmax
        :param string: string to elongate, default None
        :param lengthmin: minimal length of text, default 1
        :param lengthmax: maximal length of text, default 500
        :return: generated text
        """
        length = random.randint(lengthmin, lengthmax)
        if string is None:
            string = self._get_primer()
        is_end_of_text = False
        for _ in range(length):
            string, is_end_of_text = self._elongate(string, ignore_none=True)
        else:
            while (string[-1] not in ['.', '!', '?']) and (is_end_of_text is False):
                string, is_end_of_text = self._elongate(string)
        return string

    def generate(self, string: str = None, **kwargs) -> str:
        """
        Generates text from primer string (if given)
        :param string: string to elongate, default None
        :return: generated text
        """
        if string is None:
            string = self._get_primer()
        is_end_of_text = False
        while is_end_of_text is False:
            string, is_end_of_text = self._elongate(string, **kwargs)
        return string


class Model(Markov):
    """
    Markov class, but with additional chat-aimed functional
        answer_chance - chance of answering to messages in chat
        last_answer_time - timestamp of the last answer
    """

    def __init__(self, order: int = None, rand_coeff: int = 10, is_main: bool = False):
        """
        :param order: size of chain's window
        :param rand_coeff: coefficient of random
        :param is_main: main model or not
        """
        super().__init__(order, rand_coeff)
        self.answer_chance = 1
        self.last_answer_time = time()
        self.is_main = is_main

    def generate_answer(self, message: str):
        """
        Generates an answer text, takes message as primer
        :param message: text of message to answer
        :return: text of answer
        """
        message += ' '
        if random.random() < self.answer_chance:
            for n in self.windows:
                if len(message) >= n:
                    string = message[-n:]
                    string = self.generate(string=string, strict=True)
                    string = string[n:]
                    self.last_answer_time = time()
                    return string
                else:
                    continue
        else:
            return None

    def set_rand_coeff(self, rand_coeff: int) -> str:
        """
        Sets rand_coeff attribute
        :param rand_coeff: new rand_coeff to set
        :return: success message
        """
        self.rand_coeff = rand_coeff * 10
        self.last_answer_time = time()
        return "Успешно"

    def set_answer_chance(self, answer_chance: int) -> str:
        """
        Sets answer_chance attribute
        :param answer_chance: new answer_chance to set
        :return: success message
        """
        self.answer_chance = answer_chance / 100
        self.last_answer_time = time()
        return "Успешно"


class Manager:
    """
    Class for create and manage multiple Markov chain models
        models - dict of models, keys are model names
    """
    def __init__(self):
        self.models = {}

    def init_model(self, modelname: str, path: str, *query, last_text_enabled: bool = True,  **kwargs):
        """
        Creates model and trains it on database contents
        :param modelname: name of model
        :param path: path to database
        :param query: SQL query and substitutions dict
        :param last_text_enabled: enable last_text in model
        :param kwargs: kwargs to Model.__init__()
        """
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute(*query)

        self.models[modelname] = Model(**kwargs)
        logging.info(f'Parsing {path}: Started...')
        for elem in [i[0] for i in cursor.fetchall()]:
            self.models[modelname].parse_and_add(elem, last_text_enabled)
        logging.info(f'Parsing {path}: Completed')
        logging.info(f'Model is ready')

    def init_chat_model(self, chatid: str):
        """
        Creates a model for using in common chat
        :param chatid: chatid, will be a name of model
        """
        self.init_model(chatid,
                        config.database.messages_path,
                        '''SELECT message FROM texts WHERE userid = :userid''',
                        {'userid': chatid})

    def check_model_exists(self, chatid: str):
        """
        Checks if chat model exists, if not - creates it
        :param chatid: chatid or name of model
        """
        try:
            self.models[chatid]
        except KeyError:
            self.init_chat_model(chatid)


models_active = Manager()
