from colorama import Style


def print_colored(text, color):
    print(f"{color}{text}{Style.RESET_ALL}")