import time
from enum import Enum
from dataclasses import dataclass, field


class tokens(Enum):
    RIGHT = 'plus pointer'
    LEFT = 'min pointer'
    MOVE = 'move pointer to'
    PRINT = 'show pointer'
    FUNCTION = 'make function'
    CLOSE = 'close'
    CALL = 'run function'

    # Variable checking
    GREATER = 'greater compare between'
    LESS = 'less compare between'
    EQUAL = 'equal compare between'

    # Variable manipulation
    INCREMENT = 'increment pointer by'
    DECREMENT = 'decrement pointer by'
    MULTIPLY = 'multiply pointer by'

    # Others
    VARIABLE = ''
    EOF = str(hash(time.time_ns()))  # Impossible for the lexer to find it in a program


@dataclass
class found_token:
    token: tokens
    row: int
    content: str = field(default='')


def fixVariableTokens(checklist: list[found_token], b_index: int = 0, tmp_list=None) -> list[found_token]:
    """
    Function that reinterprets the row and checks if possible tokens has been missed
    :param checklist: List with found tokens
    :param b_index: Internally used row, should not be used
    :param tmp_list: Internally used list for checking the possible tokens, should not be used
    :return: Fixed row with the correct tokens
    """
    if tmp_list is None:
        tmp_list = []

    # Check if the b_index is larger than the checklist
    # Otherwise return the fixed row
    if len(checklist) > b_index:
        if checklist[b_index].token != tokens.VARIABLE:
            tmp_list.clear()
            return fixVariableTokens(checklist, b_index + 1, tmp_list)

        tmp_list.append(checklist[b_index])
    else:
        return checklist

    # ![Complex function alert]!
    # This function does 2 things
    # 1. Filter the tokens with more than 2 keywords (space between) <- long_token
    # 2. Return the first long_token where the first word is the same, otherwise return None
    token = next(filter(lambda long_token:
                        next(filter(lambda check_token: check_token.content == long_token.value.split(" ")[0],
                                    tmp_list), False),
                        filter(lambda all_token: all_token.value.count(" ") > 0, tokens)
                        ), None
                 )

    # If the retrieved token is None (No token could be found) try it again with an empty tmp_list
    if token is None:
        tmp_list.clear()
        return fixVariableTokens(checklist, b_index + 1, tmp_list)

    # Try to find the possible token in the tmp_list, if it goes out of bounds it will generate an IndexError,
    # That means that the token might be longer so we don't reset it
    try:
        if not any(map(lambda enum_sub: tmp_list[enum_sub[0]].content != enum_sub[1],
                       enumerate(token.value.split(" ")))):
            # Calculate the begin row of the first word
            index = b_index - len(tmp_list) + 1

            # Insert a found_token object with the correct values
            checklist.insert(
                index,
                found_token(
                    token,
                    tmp_list[0].row,
                    " ".join(map(lambda type_token: type_token.content, checklist[index: b_index + 1]))
                )
            )

            # Remove the slice from the original checklist
            del checklist[index + 1:b_index + 2]
            tmp_list.clear()

            # Go further with function with b_index at end of newly generated token
            return fixVariableTokens(checklist, b_index - (b_index - index - 1), tmp_list)

    # Catch of the IndexError exception
    except IndexError:
        pass

    # Go back with the recursive function
    return fixVariableTokens(checklist, b_index + 1, tmp_list)


def getTokens(row_words: list[str], index: int):
    if not row_words:
        return []

    current_word = row_words[0]
    new_token = next(filter(lambda token: token.value == current_word, tokens), None)
    if new_token is None:
        return [found_token(tokens.VARIABLE, index, current_word)] + getTokens(row_words[1:], index)
    else:
        return [found_token(new_token, index, current_word)] + getTokens(row_words[1:], index)


def removeSpaces(row_words: list[str]):
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


def lexer(file_content: str):
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
    found_tokens = list(map(lambda row: getTokens(row[1], row[0] + 1), enumerate(fixed_words)))
    fixed_tokens = list(map(lambda row_token: fixVariableTokens(row_token), found_tokens))
    return fixed_tokens


if __name__ == '__main__':
    with open('test.qry', 'r') as f:
        lextokens = lexer(f.read())
    print("Lexed tokens", *lextokens, sep='\n')



