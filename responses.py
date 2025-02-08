from random import choice, randint


def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'crickets...'
    elif 'hello' in lowered:
        return 'Hello there!'
    elif 'how are you' in lowered:
        return 'I\'m gggggggreat!'
    elif 'roll dice' in lowered:
        return f'You rolled: {randint(1, 20)}'
    else:
        return choice(['fucking pigeons...',
                       'No you are!',
                       'catch me outside!'])
