import time
from enum import Enum
from typing import List, Union, Tuple
from dataclasses import dataclass, field


class tokens(Enum):
    RIGHT_MEM = 'plus memory pointer by'
    RIGHT_INS = 'plus instruction pointer by'
    LEFT_MEM = 'min memory pointer by'
    LEFT_INS = 'min instruction pointer by'
    MOVE_MEM = 'move memory pointer to'
    MOVE_INS = 'move instruction pointer to'
    PRINT = 'show memory'
    FUNCTION = 'make function'
    CLOSE = 'close function'
    CALL = 'run function'
    EXIT = 'exit'
    COMMENT = '~'

    # Variable checking
    GREATER = 'greater compare between'
    LESS = 'less compare between'
    EQUAL = 'equal compare between'

    # Variable manipulation
    INCREMENT = 'increment memory pointer by'
    DECREMENT = 'decrement memory pointer by'
    MULTIPLY = 'multiply memory pointer by'

    # Others
    VARIABLE = ''
    EOF = str(hash(time.time_ns()))  # Impossible for the lexer to find it in a program


@dataclass
class found_token:
    token: tokens
    row: int
    content: str = field(default='')


def fixVariableTokens(checklist: List[found_token], b_index: int = 0, tmp_list=None) -> List[found_token]:
    """
    Function that reinterprets the row and checks if possible longer tokens has been missed
    :param checklist: List with found tokens
    :param b_index: Internally used row, should not be used
    :param tmp_list: Internally used list for checking the possible tokens, should not be used
    :return: Fixed row with the correct tokens
    """
    # If tmp_list is not a list, make it a list
    if tmp_list is None:
        tmp_list = []

    # Check if the b_index is larger than the checklist
    # Otherwise return the fixed row
    if len(checklist) <= b_index:
        return checklist

    # Append a found_token in the checklist
    tmp_list.append(checklist[b_index])

    # Get all possible longer tokens
    long_tokens: List[tokens] = list(filter(
        lambda poss_token: poss_token.value.count(" ") == len(tmp_list) - 1, tokens
    ))
    # Get the strings of all the tokens for easier comparing
    long_tokens_str: List[List[str]] = list(map(
        lambda long_token: long_token.value.split(" "), long_tokens
    ))
    # Get the string of the check tmp_list
    token_str: List[str] = list(map(
        lambda a_token: a_token.content, tmp_list
    ))
    # Try to find a token in the possible longer tokens, otherwise return None
    possible_token: Union[None, Tuple[str, tokens]] = next(filter(
        lambda long_token: token_str == long_token[0], zip(long_tokens_str, long_tokens)
    ), None)

    # If the retrieved token is None try again with the next found_token
    if possible_token is None:
        return fixVariableTokens(checklist, b_index + 1, tmp_list)

    # Insert newly found token into the list
    checklist.insert(
        b_index + 1,
        found_token(
            possible_token[1],
            checklist[b_index].row,
            " ".join(token_str)
        )
    )
    # Remove the old VARIABLE tokens so only the newly inserted token will be left
    del checklist[b_index - (len(tmp_list) - 1): b_index + 1]

    # Go back with the recursive function
    return fixVariableTokens(checklist, b_index + 1, tmp_list)


def getTokens(row_words: List[str], index: int) -> List[found_token]:
    """
    Generate from a row of strings found_token objects with the
    :param row_words:
    :param index:
    :return:
    """
    if not row_words:
        return []

    current_word = row_words[0]
    new_token = next(filter(lambda token: token.value == current_word, tokens), None)
    if new_token is None:
        return [found_token(tokens.VARIABLE, index, current_word)] + getTokens(row_words[1:], index)
    else:
        return [found_token(new_token, index, current_word)] + getTokens(row_words[1:], index)


def removeSpaces(row_words: List[str]) -> Union[None, List[str]]:
    """
    Find the first string which is not space
    :param row_words: Row of words which needs to be filtered
    :return: Filtered list where the first row is a wordt and no space
    """
    if not row_words:
        return None
    elif (word := row_words[0]).isspace() or not word:
        return removeSpaces(row_words[1:])
    return row_words


def lexer(file_content: str) -> List[List[found_token]]:
    """
    Run the lexer on the given content of a file.
    :param file_content: Content of the file which needs lexing
    :return: A 2d list with all the tokens per row
    """
    if not file_content:
        return []

    lines = file_content.splitlines(keepends=False)
    words = list(map(lambda word: word.split(' '), lines))
    fixed_words = list(filter(
        lambda word: word is not None,
        map(lambda line: removeSpaces(line), words))
    )
    remove_comments = list(filter(lambda row: row[0] != tokens.COMMENT.value, fixed_words))
    found_tokens = list(map(lambda row: getTokens(row[1], row[0] + 1), enumerate(remove_comments)))
    fixed_tokens = list(map(lambda row_token: fixVariableTokens(row_token), found_tokens))
    return fixed_tokens

