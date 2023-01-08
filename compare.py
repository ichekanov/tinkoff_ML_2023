import argparse
import ast
import logging
import sys
import time
import numpy as np


class Spinner:
    """
    Implements a cool spinner with progress in percents.
    """

    def __init__(self, overall_count: int, delay: float = 0.1):
        """
        Parameters
        overall_count : int
            Number of tick() calls to complete the spinner.
        delay : float
            Delay between spinner changes in seconds.
        """
        self._spinner_generator = self.__spinning_cursor()
        self._delay = delay
        self._prev_spin = time.time()
        self._prev_length = 0
        self._overall_count = overall_count
        self._counter = 0

    def __spinning_cursor(self):
        """
        Generator for spinner.
        """
        while True:
            for cursor in '|/-\\':
                yield cursor

    def tick(self):
        """
        Function to call on each tick.
        Every call increases the progress by 1/overall_count.
        """
        self._counter += 1
        if time.time() - self._prev_spin < self._delay:
            return
        self._prev_spin = time.time()
        sys.stdout.write('\b'*self._prev_length)
        progress = self._counter / self._overall_count * 100
        new_spinner: str = next(self._spinner_generator)
        new_spinner += f' {progress:.0f}%'
        self._prev_length = len(new_spinner)
        sys.stdout.write(new_spinner)
        sys.stdout.flush()

    def finish(self):
        """
        Function to call when spinner is finished.
        Removes the spinner from the console.
        """
        sys.stdout.write('\b'*self._prev_length)
        sys.stdout.flush()


def prepare_text(text: str) -> str:
    """
    Function prepares text for comparison.

    Parameters
    text : str
        Text to prepare.

    Returns
    str
        Prepared text.
    """
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            node.value.s = '' # remove docstring
    new_text = ast.unparse(tree)  # recreate text from AST
    new_text = new_text.replace('"""', '')  # remove all docstrings quotes
    new_text = new_text.replace('\n', ' ')  # remove all newlines
    new_text = new_text.replace('\t', '')  # remove all tabs
    new_text = new_text.replace('  ', '')  # remove all indents
    new_text = new_text.replace('\'', '"')  # replace all ' with "
    new_text = new_text.lower()  # make all letters lowercase
    return new_text


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Function calculates Levenshtein distance between two strings.

    Parameters
    s1 : str
        First string.
    s2 : str
        Second string.

    Returns
    int
        Levenshtein distance.
    """
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    logging.debug(f"Length of the first string: {len(s1)}")
    logging.debug(f"Length of the second string: {len(s2)}")
    distances = range(len(s1) + 1)
    spinner = Spinner(len(s2))
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        # I tried to initialize array with [i2+1] + [0] * len(s1) but it turned out to be slower
        # Also, I tried to use numpy arrays, but it was twice slower than the code below
        # (you can find this version in previous commits)
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(
                    1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
        spinner.tick()
    spinner.finish()
    logging.debug(f"Levenshtein distance: {distances[-1]}")
    return distances[-1]


def compare(file1: str, file2: str) -> float:
    """
    Function compares two files and returns the equality rate.

    Parameters
    file1 : str
        Path to the first file.
    file2 : str
        Path to the second file.

    Returns
    float
        Normalized distance between two files.
    """
    with open(file1, "r", encoding="utf-8") as file:
        text1 = file.read()
        text1 = prepare_text(text1)
    with open(file2, "r", encoding="utf-8") as file:
        text2 = file.read()
        text2 = prepare_text(text2)
    distance = levenshtein_distance(text1, text2) / max(len(text1), len(text2))
    return round(1-distance, 3)


def main(input_file: str, output_file: str) -> None:
    """
    Function compares all pairs of files from input_file and writes the results to output_file.

    Parameters
    input_file : str
        Path to the input file.
    output_file : str
        Path to the output file.
    """
    start = time.time()
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s - %(levelname)s - %(message)s",
                        datefmt="%d-%b-%y %H:%M:%S")
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    logging.info(f"Found {len(lines)} file pairs in {input_file}")
    results = []
    for line in lines:
        logging.info(f"Processing files: {line}")
        try:
            file1, file2 = (m.strip() for m in line.split())
            distance = compare(file1, file2)
        except ValueError:
            logging.error(f"Incorrect line: {line}")
            distance = -1.0
        except FileNotFoundError:
            logging.error(f"One of files not found: {line}")
            distance = -1.0
        logging.info(f"Similarity: {distance}")
        results.append(distance)
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(map(str, results)))
    logging.info(f"Successfully saved {len(results)} results to {output_file}")
    logging.info(f"Total time elapsed: {round(time.time() - start, 2)}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to the input file.", type=str)
    parser.add_argument("output_file", help="Path to the output file.", type=str)
    args = parser.parse_args()
    main(args.input_file, args.output_file)
    # main("input.txt", "output.txt")
