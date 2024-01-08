import argparse
import webbrowser
import re
import sys
import time

from math import ceil
from pathlib import Path
from random import choice
from time import sleep
from sys import stdin
from io import BytesIO

from PIL import Image, ImageChops, UnidentifiedImageError
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from rich.console import Console


def resize_image(image, new_width=100):
    """
    Resizes an image preserving the aspect ratio.
    Adjusts height considering ASCII character proportions.
    """
    original_width, original_height = image.size
    aspect_ratio = original_height / original_width
    new_height = int(aspect_ratio / 2 * new_width)
    return image.resize((new_width, new_height))


def convert_image_to_grayscale(image):
    """Converts an image to grayscale."""
    return image.convert("L")


def create_colored_image_matrix(image, new_width=500, new_height=500):
    """Creates a new image with colored ASCII characters."""

    image = image.resize((new_width, new_height))
    image = convert_image_to_grayscale(image)
    pixels = list(image.getdata())

    # Original ASCII color choices
    ascii_colors = {
        "pink": "\033[1;35m",
        "blue": "\033[1;34m",
        "yellow": "\033[1;33m",
        "green": "\033[1;32m",
        "red": "\033[1;31m",
        "slate": "\033[1;30m"
    }
    
    # Convert pixels to ASCII color chars
    ascii_color_chars = [ascii_colors[int(pixel / 86)] for pixel in pixels]
    
    # Construct 2D array for new image
    image_matrix = []
    for row in range(new_height):
        start = row * new_width
        end = start + new_width
        image_matrix.append(ascii_color_chars[start:end])

    return image_matrix



def draw_ascii_art(image_ascii, new_width=100):
    """Draws ASCII art with colors."""
    ascii_chars = list(image_ascii)
    new_height = len(ascii_chars) // new_width

    color_palette = {
        "pink": "\033[1;35m",    
        "blue": "\033[1;34m",
        "yellow": "\033[1;33m",
        "green": "\033[1;32m",
        "red": "\033[1;31m",
        "slate": "\033[1;30m"
    }

    for row in range(new_height):
        if row % 2 == 0:
            color = color_palette["red"]
        elif row % 3 == 0:
            color = color_palette["yellow"]
        else:
            color = color_palette["slate"]
        
        for col in range(new_width):
            time.sleep(0.003)
            sys.stdout.write(color)
            sys.stdout.write(ascii_chars[row * new_width + col])
            sys.stdout.flush()


def map_pixels_to_ascii_chars(image, range_width, ascii_chars):
    """Maps each pixel to an ascii character based on the range in which it lies."""
    pixels = list(image.getdata())
    return [ascii_chars[int(pixel / range_width)] for pixel in pixels]


def convert_image_to_ascii_art(image, ascii_chars, range_width, new_width=100, fix_aspect_ratio=False):
    """
    Converts an image to ASCII art.
    Adjusts aspect ratio if fix_aspect_ratio is True.
    """
    image = resize_image(image)
    image = convert_image_to_grayscale(image)

    ascii_chars = map_pixels_to_ascii_chars(image, range_width, ascii_chars)
    ascii_art_lines = [
        "".join(ascii_chars[index: index + new_width])
        for index in range(0, len(ascii_chars), new_width)
    ]

    if fix_aspect_ratio:
        # The generated ASCII image is approximately 1.35 times
        # larger than the original image
        # So, we will drop one line after every 3 lines
        image_ascii = [char for index, char in enumerate(ascii_art_lines) if index % 4 != 0]

    return "\n".join(ascii_art_lines)


def single_ascii_replacement(image_ascii, single_ascii_char):
    """Count frequency of each character in the input string"""
    char_freq = {}
    for char in image_ascii:
        if char not in char_freq:
            char_freq[char] = 0
        char_freq[char] += 1

    # Find the most frequent character (excluding newline character)
    most_freq_char = max(char_freq, key=lambda k: (char_freq[k], k != '\n'))

    # Replace the most frequent character with space
    image_ascii = image_ascii.replace(most_freq_char, ' ')

    # Replace all other characters with the specified single character
    return ''.join(single_ascii_char if char != ' ' and char != '\n' else char for char in image_ascii)


def hype(console):
    """Prints a dummy progress bar for user engagement."""
    
    verbs = [
        "Articulating",
        "Coordinating",
        "Gathering",
        "Powering up",
        "Clicking on",
        "Backing up",
        "Extrapolating",
        "Authenticating",
        "Recovering",
        "Finalizing",
        "Testing",
        "Upgrading",
        "Launching",
        "Logging",
        "Scanning",
        "Setting up",
        "Tracking",
        "Finding",
        "Cloning",
        "Forking",
        "Booting up",
        "Loading in",
    ]

    nouns = [
        "scope",
        "lunch",
        "meetings",
        "skeletons",
        "devices",
        "margins",
        "bookmarks",
        "CPUs",
        "folders",
        "emails",
        "disks",
        "JPEGs",
        "ROMs",
        "RAMs",
        "repositories",
        "viruses",
        "messages",
        "errors",
        "progress bar",
        "users",
    ]

    # To print beautiful dummy progress bar to the user
    with console.status("[bold green]Turning your image into ASCII art..."):
        for _ in range(4):
            console.log(f"{choice(verbs)} {choice(nouns)}...")
            sleep(1)
        sleep(1)
    console.log("[bold green]Here we go...!")


def welcome_message(console):
    """Prints a welcome message to the console."""
    console.print("[bold yellow] Welcome to ASCII ART Generator!")


def handle_black_yellow(image):
    """Using the new function to create a colored image matrix"""
    image_matrix = create_colored_image_matrix(image)
    smiley = Image.new("RGB", (500, 500))
    for row in range(500):
        for col in range(500):
            smiley.putpixel((col, row), image_matrix[row][col])
    return smiley.show()


def handle_image_print(image_ascii, color=None):
    """Handles printing of ASCII art to the console."""
    console = Console()

    welcome_message(console)

    hype(console)

    # print the ASCII art to the console.
    if color:
        console.print(image_ascii, style=color)
    else:
        console.print(image_ascii)


def inverse_image_color(image):
    """Inverts the color of the image."""
    return ImageChops.invert(image)


def handle_image_conversion(image, range_width, ascii_chars, inverse_color):
    """
    Handles the conversion of an image to ASCII art.
    """
    if inverse_color:
        image = inverse_image_color(image)

    image_ascii = convert_image_to_ascii_art(
        image, range_width=range_width, ascii_chars=ascii_chars, fix_aspect_ratio=False
    )

    return image_ascii



def init_args_parser():
    """Initializes and returns the argument parser."""
    parser = argparse.ArgumentParser()
    charset_group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        dest="image_file_path", 
        nargs="?", 
        type=str, 
        help="Image file path."
    )

    parser.add_argument(
        dest="stdin",
        nargs="?",
        type=argparse.FileType("rb"),
        help="Read image from stdin.",
        default=stdin,
    )

    charset_group.add_argument(
        "--preset",
        dest="preset",
        type=int,
        choices=[1, 2],
        help="Select 1 or 2 for predefined ASCII character sets.",
    )

    charset_group.add_argument(
        "--charset",
        dest="charset",
        nargs="+",
        help="A list of characters to display the image, from darkest to brightest.",
    )

    charset_group.add_argument(
        "--black-yellow",
        dest="black_yellow",
        action="store_true",
        help="Output a black and yellow image. Does not work if a character set was already chosen.",
    )

    parser.add_argument(
        "--inverse", 
        dest="inverse_image", 
        action="store_true", 
        default=False
    )

    parser.add_argument(
        "--color",
        dest="color",
        type=str,
        help=(
            "Add color to your ASCII art by mentioning a color after --color. "
            "It also supports hexadecimal notation that can help you to choose more colors."
        ),
    )

    parser.add_argument(
        "--store",
        dest="store_art",
        type=Path,
        help=(
            "Save the ASCII art of the image to a given path, e.g., --store output.txt. "
            "The result will be great if you choose a .svg file extension."
        ),
    )

    parser.add_argument(
        "--single-ascii_char",
        dest="single_ascii_char",
        type=str,
        help=(
            "A single ASCII character to display the image. "
            "It uses existing default preset character to convert it into single."
        ),
    )

    parser.add_argument(
        "--drawing",
        action='store_true',
        help=(
            "It will draw an image with multiple characters. "
        ),
    )

    return parser.parse_args()


def get_predefined_charset(preset=1):
    """Returns a predefined set of ASCII characters based on the chosen preset."""
    
    if preset == 1:
        return [" ", ".", "°", "*", "o", "O", "#", "@"]
    if preset == 2:
        return ["#", "?", "%", ".", "S", "+", ".", "*", ":", ",", "@"]
    raise ValueError("Preset character sets are either 1 or 2.")


def read_image_from_stdin(buffer):
    """Reads image from stdin."""
    buffer = buffer.read()
    return Image.open(BytesIO(buffer))


def ask_user_for_image_path_until_success(get_image):
    """Asks user for a path to base image."""
    image = None
    while True:
        try:
            image = get_image()
        except FileNotFoundError:
            print("The specified path does not exist, please try again.")
            return ask_user_for_image_path_until_success(
                lambda: Image.open(prompt("> ", completer=PathCompleter()))
            )
        except UnidentifiedImageError:
            print("The specified path is not of a valid image, please try again.")
            return ask_user_for_image_path_until_success(
                lambda: Image.open(prompt("> ", completer=PathCompleter()))
            )
        except AttributeError:
            print("The specified path is not of a valid image, please try again.")
            return ask_user_for_image_path_until_success(
                lambda: Image.open(prompt("> ", completer=PathCompleter()))
            )
        except IsADirectoryError:
            print("The specified path is not of a valid image, please try again.")
            return ask_user_for_image_path_until_success(
                lambda: Image.open(prompt("> ", completer=PathCompleter()))
        )
        except KeyboardInterrupt:
            print("Are you sure you want to quit Y/N : ")
            input = prompt("> ")
            if input.upper() =='Y' :
                sys.exit()
            else :
                print("The specified path is not of a valid image, please try again.")
                return ask_user_for_image_path_until_success(
                    lambda: Image.open(prompt("> ", completer=PathCompleter()))
        )

        else:
            return image


def read_image_from_path(path=None):
    """
    Reads and returns an image from the given path.
    Handles common errors and prompts the user until a valid image is provided.
    """
    if path:
        return ask_user_for_image_path_until_success(lambda: Image.open(path))
    else:
        print(
            "No path specified as argument, please type a path to an image or Ctrl-C to quit."
        )
        return ask_user_for_image_path_until_success(
            lambda: Image.open(prompt("> ", completer=PathCompleter()))
        )


def handle_store_art(path, image_ascii, color):
    """
    Handles storing the ASCII art in a file.
    """
    try:
        if path.suffix in (".txt", ".svg"):
            with open(path, "wt") as report_file:
                console = Console(style=color, file=report_file, record=True)
                if path.suffix == ".svg":
                    if color:
                        console.print(image_ascii, style=color)
                        console.save_svg(path, title="ZTM ASCII Art 2022")
                        webbrowser.open(f"file://{path.absolute()}", new=1)
                elif color:
                    console.print(image_ascii, style=color)
                else:
                    console.print(image_ascii)
        else:
            raise Exception("The file extension did not match as txt file!")
    except Exception as e:
        print(e)
        print(
            "\33[101mOops, you have chosen the wrong file extension. Please give a svg file name e.g., output.txt \033[0m"
        )


def main():
    """
    Main function to execute the ASCII art generator.
    """
    args = init_args_parser()

    if not args.stdin.isatty():
        #image = read_image_from_stdin(args.stdin.buffer)
        image = read_image_from_stdin(args.stdin)
    else:
        image = read_image_from_path(args.image_file_path)

    if args.preset:
        ascii_chars = get_predefined_charset(args.preset)
    elif args.charset:
        print(f"Using custom character set: {', '.join(args.charset)}")
        ascii_chars = args.charset
    else:
        ascii_chars = get_predefined_charset()

    # as the range width is based on the number of ASCII_CHARS we have
    range_width = ceil((255 + 1) / len(ascii_chars))

    # convert the image to ASCII art
    if args.black_yellow:
        handle_black_yellow(image)
        return

    image_ascii = handle_image_conversion(
        image, range_width, ascii_chars, args.inverse_image
    )
    if args.single_ascii_char:
        image_ascii = single_ascii_replacement(image_ascii, args.single_ascii_char)
    
    if args.drawing:
        drawing(image_ascii)
        print("\n")
        return
    # display the ASCII art to the console
    handle_image_print(image_ascii, args.color)

    ### Save the image ###
    if args.store_art:
        handle_store_art(args.store_art, image_ascii, args.color)


if __name__ == "__main__":
    main()
