import logging
import random
import sqlite3


class Markov:
    """
    order - number of characters in window,
    rand_coeff - random coefficient
    """
    def __init__(self, order=None, rand_coeff=10):
        self.matrix = {}
        if order is None:
            self.windows = [9, 6, 3, 1]
        else:
            self.windows = [order, 9, 6, 3, 1]
        self.N = self.windows[0]
        self.last_text = ' ' * self.N
        self.rand_coeff = rand_coeff

    def _make_pairs(self, text):
        """
        Makes pairs
        """
        for n in self.windows:
            if len(text) < n:
                continue
            else:
                yield '_START', text[:n]
                text = (self.last_text + ' ' + text).strip()
                self.last_text = text[-n:]
                break
        for n in self.windows:
            if len(text) < n:
                continue
            else:
                for i in range(len(text)):
                    if i < (len(text) - n):
                        first, second = text[i: i+n], text[i+n]
                        yield first, second
                    else:
                        first, second = text[i: i+n], None
                        yield first, second
                        break

    def parse_and_add(self, text):
        """
        Parses text and adds to statistic matrix
        """
        for i in self._make_pairs(text):
            try:
                self.matrix[i[0]][i[1]] += 1
            except KeyError:
                try:
                    self.matrix[i[0]][i[1]] = 1
                except KeyError:
                    self.matrix[i[0]] = {i[1]: 1}

    def _get_primer(self):
        """
        Returns first characters of text to elongate
        """
        try:
            primer = random.\
                choices(list(self.matrix['_START'].keys()), weights=list(self.matrix['_START'].values()))[0]
        except KeyError:
            primer = 'Недостаточно данных для генерациии сообщений.\
                        \nБот учится на ваших сообщениях, напишите что-нибудь!'
        return primer

    def _elongate(self, primer, ignore_none=False, strict=False):
        """
        Elongates the given primer by 1 char
        Returns elongated string and is_end_of_text (True/False)
        """
        for n in self.windows:
            if primer[-n:] in self.matrix:
                if random.randint(1, 1000) > self.rand_coeff:
                    next_char = random.choices(list(self.matrix[primer[-n:]].keys()),
                                               list(self.matrix[primer[-n:]].values()))[0]
                else:
                    next_char = random.choice(list(self.matrix.keys()))

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
                            return primer + next_char, False
                        else:
                            return primer, True
                else:
                    return primer + next_char, False
            else:
                continue
        else:
            if strict is True:
                return primer + self._get_primer(), False
            else:
                return primer, True

    def generate_l(self, string=None, lengthmin=1, lengthmax=500):
        """
        Generates text from primer string (if given) with specified max and min length
        """
        length = random.randint(lengthmin, lengthmax)
        if string is None:
            string = self._get_primer()
        is_end_of_text = False
        for _ in range(length):
            string, is_end_of_text = self._elongate(string, ignore_none=random.choice([True, False]))
        else:
            while (string[-1] not in ['.', '!', '?']) and (is_end_of_text is False):
                string, is_end_of_text = self._elongate(string)
        return string

    def generate(self, string=None, **kwargs):
        """
        Generates text from primer string (if given)
        """
        if string is None:
            string = self._get_primer()
        is_end_of_text = False
        while is_end_of_text is False:
            string, is_end_of_text = self._elongate(string, **kwargs)
        return string

    # def generate_answer(self, message):
    #     """
    #     Generates an answer, takes message text as primer
    #     """
    #     message += ' '
    #     for n in self.windows:
    #         if len(message) < n:
    #             continue
    #         else:
    #             string = message[-n:]
    #             is_end_of_text = False
    #             while is_end_of_text is False:
    #                 string, is_end_of_text = self._elongate(string, strict=True)
    #             string = string[n:]
    #             return string


class Model(Markov):
    """
    order - number of characters in window,
    rand_coeff - random coefficient
    """
    def __init__(self, order=None, rand_coeff=10):
        super().__init__(order, rand_coeff)
        self.answer_chance = 1

    def generate_answer(self, message):
        """
        Generates an answer text, takes message as primer
        """
        message += ' '
        for n in self.windows:
            if len(message) < n:
                continue
            else:
                string = message[-n:]
                string = self.generate(string=string, strict=True)
                string = string[n:]
                return string

    def set_rand_coeff(self, rand_coeff):
        self.rand_coeff = rand_coeff
        return "Успешно"

    def set_answer_chance(self, answer_chance):
        self.answer_chance = answer_chance/100
        return "Успешно"


class Manager:

    def __init__(self):
        self.models = {}

    def init_model(self, modelname, path, *query, **kwargs):
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute(*query)

        self.models[modelname] = Model(**kwargs)
        logging.info(f'Parsing {path}: Started...')
        for elem in [i[0] for i in cursor.fetchall()]:
            self.models[modelname].parse_and_add(elem)
        logging.info(f'Parsing {path}: Completed')
        logging.info(f'Model is ready')

    def init_chat_model(self, chatid):
        self.init_model(chatid,
                        r'database\messages.db',
                        '''SELECT message FROM texts WHERE userid = :userid''',
                        {'userid': chatid})

    def check_model_exists(self, chatid):
        try:
            self.models[chatid]
        except KeyError:
            self.init_chat_model(chatid)
