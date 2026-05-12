'''Caesar cipher decoder script.

Reads encrypted text from password.txt, prints all possible Caesar-decoded
results, and saves the chosen result to result.txt.
'''

import os

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
PASSWORD_FILE = 'password.txt'
RESULT_FILE = 'result.txt'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASSWORD_FILE_PATH = os.path.join(BASE_DIR, PASSWORD_FILE)
RESULT_FILE_PATH = os.path.join(BASE_DIR, RESULT_FILE)
TEXT_DICTIONARY = {
    'mars',
    'base',
    'door',
    'open',
    'password',
    'engineer',
    'rome',
    'caesar',
    'storage',
    'emergency',
    'secret',
    'key',
}


def caesar_cipher_decode(target_text):
    '''Decode the target text with every Caesar shift and print each result.'''
    decoded_results = []

    for shift in range(len(ALPHABET)):
        decoded_text = ''

        for char in target_text:
            if char.lower() in ALPHABET:
                original_index = ALPHABET.index(char.lower())
                decoded_index = (original_index - shift) % len(ALPHABET)
                decoded_char = ALPHABET[decoded_index]

                if char.isupper():
                    decoded_text += decoded_char.upper()
                else:
                    decoded_text += decoded_char
            else:
                decoded_text += char

        decoded_results.append((shift, decoded_text))
        print(f'{shift:2d}번째 자리수: {decoded_text}')

        if contains_dictionary_word(decoded_text):
            print('사전 단어가 발견되어 자동 식별 후보로 표시합니다.')
            print(f'후보 자리수: {shift}')
            break

    return decoded_results


def contains_dictionary_word(text):
    '''Return True when any dictionary word appears in the text.'''
    normalized_text = text.lower()

    for word in TEXT_DICTIONARY:
        if word in normalized_text:
            return True

    return False


def read_password_file(file_name):
    '''Read encrypted text from file with exception handling.'''
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f'오류: {file_name} 파일을 찾을 수 없습니다.')
    except PermissionError:
        print(f'오류: {file_name} 파일에 접근할 권한이 없습니다.')
    except OSError as error:
        print(f'오류: {file_name} 파일을 읽는 중 문제가 발생했습니다: {error}')

    return ''


def save_result_file(file_name, decoded_text):
    '''Save decoded result to file with exception handling.'''
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(decoded_text)
    except PermissionError:
        print(f'오류: {file_name} 파일에 저장할 권한이 없습니다.')
        return False
    except OSError as error:
        print(f'오류: {file_name} 파일을 저장하는 중 문제가 발생했습니다: {error}')
        return False

    return True


def choose_result(decoded_results):
    '''Ask the user which shift is correct and return the decoded text.'''
    if not decoded_results:
        return ''

    while True:
        user_input = input('해독된 번호를 입력하세요: ').strip()

        if not user_input:
            print('번호를 입력해 주세요.')
            continue

        if not user_input.isdigit():
            print('숫자만 입력해 주세요.')
            continue

        selected_shift = int(user_input)

        for shift, decoded_text in decoded_results:
            if shift == selected_shift:
                return decoded_text

        print('출력된 번호 중에서 다시 입력해 주세요.')


def main():
    '''Run the Caesar cipher decoding workflow.'''
    encrypted_text = read_password_file(PASSWORD_FILE_PATH)

    if not encrypted_text:
        print('해독할 문자열이 없습니다.')
        return

    print(f'암호문: {encrypted_text}')
    decoded_results = caesar_cipher_decode(encrypted_text)
    selected_result = choose_result(decoded_results)

    if not selected_result:
        print('선택된 해독 결과가 없습니다.')
        return

    if save_result_file(RESULT_FILE_PATH, selected_result):
        print(f'최종 암호가 {RESULT_FILE_PATH} 파일에 저장되었습니다.')
        print(f'선택된 해독 결과: {selected_result}')


if __name__ == '__main__':
    main()