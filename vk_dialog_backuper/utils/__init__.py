from .logger import logger
from .docopt import docopt


def ask_yes_or_no(question, true_answer='y', false_answer='n', default_answer='', default=True):
    true_answer = true_answer.lower()
    false_answer = false_answer.lower()
    default_answer = default_answer.lower()

    output = question.strip() + ' (' + (true_answer.upper() + '/' + false_answer if default else
                                        true_answer + '/' + false_answer.upper()) + '): '

    answer = None
    while answer not in (true_answer, false_answer, default_answer):
        answer = input(output).lower()

    if answer == true_answer:
        return True
    elif answer == false_answer:
        return False
    else:
        return default
