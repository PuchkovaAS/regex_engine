import itertools
import sys
from enum import Enum
from functools import reduce

sys.setrecursionlimit(10000)


class ReWord(Enum):
    NOTHING = 0
    START = 1
    END = 2
    ALL = 3
    RET_TRUE = 4


class RePlace(Enum):
    PLUS = 0
    MUL = 1
    ASK = 2


class Regex:

    def __init__(self, regex, word):
        anchor, regex_edit = self.check_anchor(regex)

        words_for_cheking = self.get_all_variant(regex_edit, word)
        self.cheking_words(anchor, word, words_for_cheking)

    def cheking_words(self, anchor, word, words_for_cheking):
        for regex_edit in words_for_cheking:
            common_res = False
            if anchor == ReWord.RET_TRUE:
                common_res = True
            elif anchor == ReWord.NOTHING:
                common_res = self.check_all(regex=regex_edit, word=word)
            elif anchor == ReWord.ALL:
                if len(regex_edit) != len(word):
                    common_res = False
                else:
                    common_res = self.check_regex(regex=regex_edit, word=word)
            elif anchor == ReWord.START:
                real_wight = self.get_real_wight(regex_edit)
                common_res = self.check_regex(regex=regex_edit, word=word[0:real_wight])
            elif anchor == ReWord.END:
                real_wight = self.get_real_wight(regex_edit)
                common_res = self.check_regex(regex=regex_edit, word=word[len(word) - real_wight:len(word)])
            if common_res:
                print(True)
                return
        print(False)

    @staticmethod
    def get_real_wight(regex):
        count = 0
        i = 0
        while i < len(regex):
            if regex[i] == '\\':
                i += 2
            else:
                i += 1
            count += 1
        return count

    def get_all_variant(self, regex, words):
        if set("+*?").isdisjoint(regex):
            return [regex]
        res = []
        letter_off = []
        dict_symbl = {'*': RePlace.MUL, '+': RePlace.PLUS, '?': RePlace.ASK}
        for index, letter in enumerate(regex):
            if letter in dict_symbl.keys() and (index == 0 or regex[index - 1] != '\\'):
                res.append(dict_symbl[letter])
                letter_off.append(regex[index - 1:index + 1])

        if letter_off:
            count_normal = len(regex) - reduce(lambda a, b: a + b, map(len, letter_off))
        else:
            count_normal = len(regex)

        variant = self.summs(list(range(len(words) - count_normal + 1)), res, *range(len(words) - count_normal + 1))

        result_words = []
        for element in variant:
            new_regex = regex
            for rex, templ in zip(element, letter_off):
                new_regex = new_regex.replace(templ, rex * templ[0], 1)
                result_words.append(new_regex)
        if not result_words:
            return [regex]
        return result_words

    @staticmethod
    def get_start_index(word, templ):
        for ind, liter in enumerate(word):
            if liter == templ and (ind == 0 or word(ind - 1) != '\\'):
                return ind

    @staticmethod
    def check_regex(regex, word):
        index_re = 0
        index_word = 0
        while index_re < len(regex):
            if regex[index_re] == '.' and (index_re == 0 or regex[index_re - 1] != '\\'):
                index_re += 1
                index_word += 1
            elif regex[index_re] == '\\':
                index_re += 1
            elif len(word) == index_word or regex[index_re] != word[index_word]:
                return False
            else:
                index_re += 1
                index_word += 1
        return True

    def check_all(self, regex, word):
        count_letter = self.get_real_wight(regex)
        for ind in range(len(word) - count_letter + 1):
            result = self.check_regex(regex, word[ind:ind + count_letter])
            if result:
                return True
        return False

    @staticmethod
    def check_anchor(regex):
        if len(regex) == 0:
            return ReWord.RET_TRUE, regex

        if regex[0] == '^' and regex[-1] == '$':
            return ReWord.ALL, regex[1:-1]

        if regex[0] == '^':
            return ReWord.START, regex[1:len(regex)]

        if regex[-1] == '$':
            return ReWord.END, regex[0:-1]

        return ReWord.NOTHING, regex

    @staticmethod
    def check_value(counts, value):
        for c1, v1 in zip(counts, value):
            if c1 == RePlace.PLUS and v1 < 1:
                return False
            if c1 == RePlace.MUL and v1 < 0:
                return False
            if c1 == RePlace.ASK and v1 not in [0, 1]:
                return False
        return True

    def summs(self, answers, counts, *dig):
        res = []
        if not counts:
            return res
        for answer in answers:
            for i in range(1, answer + 1):
                for j in itertools.combinations_with_replacement(list(dig), i):
                    if len(list(j)) != len(counts):
                        continue
                    if sum(list(j)) == answer:
                        wq1 = itertools.permutations(j)
                        for val in wq1:
                            if val not in res and self.check_value(counts, val):
                                res.append(val)
        if not res:
            return [[0 if count != RePlace.PLUS else 1 for count in counts]]

        return res


regex_in, word_in = input().split("|")
new_re = Regex(regex=regex_in, word=word_in)
