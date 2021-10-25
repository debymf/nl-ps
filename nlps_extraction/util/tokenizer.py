import regex
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from loguru import logger
from tqdm import tqdm
import string
import random
from transformers import BertTokenizer

stop_words = stopwords.words("english")


def tokenize_exp_as_symbols_dict(statement_dict):
    statements = dict()
    masking = dict()
    for title, content in tqdm(statement_dict.items()):
        tokenization_s, _ = tokenize_exp_as_symbols(content)
        statements[title] = tokenization_s
    return statements


def tokenize_exp_as_words_dict(statement_dict):
    return {
        title: tokenize_exp_as_words(content)
        for title, content in statement_dict.items()
    }


def get_new_variables(statement):
    split_statement = split_expressions(statement)

    variables = list()
    for element in split_statement:
        if "{{begin-" in element or element[0] == "$":
            variables.extend(get_variables(element))

    all_variables = list(set(variables))
    variable_matching = dict()
    for v in all_variables:
        if v.islower():
            variable_matching[v] = random.choice(string.ascii_lowercase)
        else:
            variable_matching[v] = random.choice(string.ascii_uppercase)

    expressions_found = regex.findall(r"(\$.*?\$)", statement)

    for e in expressions_found:
        new_e = replace_variables(e, variable_matching)
        statement = statement.replace(e, new_e)

    return statement


def replace_variables(exp, variables_dict):
    expression = exp.replace("{", "{ ").replace("}", " }").replace(" ", "  ")
    expression = expression.replace("[", "[ ").replace("]", " ]")
    expression = expression.replace(",", " , ")
    expression = expression.replace("(", "( ").replace(")", " )")
    expression = expression.replace("$", " $ ")
    variables = regex.findall(r" ([A-Za-z]) ", expression)

    for v in variables:
        expression = expression.replace(" " + v + " ", " " + variables_dict[v] + " ")

    return expression


def get_variables(exp):

    expression = exp.replace("{", "{ ").replace("}", " }").replace(" ", "  ")
    expression = expression.replace("[", "[ ").replace("]", " ]")
    expression = expression.replace(",", " , ")
    expression = expression.replace("(", "( ").replace(")", " )")
    expression = expression.replace("$", " $ ")
    variables = regex.findall(r" ([A-Za-z]) ", expression)

    return variables


def tokenize_exp_as_symbols(statement):
    masking = list()
    statement = split_expressions(statement)
    tokenized_statement = list()
    for element in statement:
        if "{{begin-" in element or element[0] == "$":
            tokenized_exp = tokenize_equation(element)
            masking = masking + ([1] * len(tokenized_exp))
            tokenized_statement.extend(tokenized_exp)
        else:
            tokenized_text = tokenize_text_part(element)
            masking = masking + ([-1] * len(tokenized_text))
            tokenized_statement.extend(tokenized_text)

    return tokenized_statement, masking


def tokenize_exp_as_symbols_bert(statement):
    expressions = list()
    words = list()
    statement = split_expressions(statement)
    for element in statement:
        if "{{begin-" in element or element[0] == "$":
            tokenized_exp = tokenize_equation(element)
            words.extend(["[MASK]"] * len(tokenized_exp))
            expressions.extend(tokenized_exp)
        else:
            tokenized_text = tokenize_text_part(element)
            expressions.extend(["[MASK]"] * len(tokenized_text))
            words.extend(tokenized_text)
    return words, expressions


def tokenize_exp_as_words(statement):
    statement = split_expressions(statement)
    tokenized_statement = list()

    for element in statement:
        if "{{begin-" in element or element[0] == "$":
            tokenized_statement.append(element)
        else:
            tokenized_statement.extend(tokenize_text_part(element))

    return tokenized_statement


def tokenize_equation(exp):

    exp = exp.lower()

    SPLIT_REGEX = [
        "(\\\\[a-z]*)",
        "(\$)",
        "(\{)",
        "(\[)",
        "(\])",
        "(\^)",
        "(\=)",
        "(\})",
        "(\()",
        "(\))",
        "(\,)",
        "(\+)",
        "(\-)",
        "(\/)",
        "(\*)",
        "(\.)",
        "(\:)",
        "(\_)",
        "[VAR]",
    ]

    expression = exp.replace("{", "{ ").replace("}", " }").replace(" ", "  ")
    expression = expression.replace("[", "[ ").replace("]", " ]")
    expression = expression.replace(",", " , ")
    expression = expression.replace("(", "( ").replace(")", " )")
    expression = expression.replace("$", " $ ")
    variables = regex.findall(r" ([A-Za-z]) ", expression)

    tmp = expression

    tmp = tmp.split(" ")
    for r in SPLIT_REGEX:
        equations = list(tmp)
        tmp = []
        for equation in equations:
            tmp.extend(regex.split(r, equation))
            tmp = list(filter(None, tmp))
    equations = list(tmp)

    return equations


def split_expressions(statement):
    statement_list = regex.compile(
        r"(.*?)(\{\{begin-.*?\}\}.*?\{\{end-.*?\}\})", regex.MULTILINE | regex.DOTALL
    ).split(statement)

    content = list()
    for element in statement_list:
        if "{{begin-" not in element:
            element_list = regex.compile(r"(.*?)(\$.*?\$)").split(element)
            content.extend(element_list)
        else:
            content.append(element)

    return clean_statement(content)


def clean_statement(statement):
    clean_statement = list()
    for element in statement:
        element = element.strip()
        if element:
            clean_statement.append(element)
    return clean_statement


def tokenize_text_part(statement_part):
    stop_words = set(stopwords.words("english"))
    tokens = word_tokenize(statement_part)

    # tokens = [token.lower().strip() for token in tokens if token not in stop_words]

    return tokens
