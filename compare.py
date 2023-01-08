import argparse
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


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Function calculate Levenshtein distance between two strings.

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
    distances = range(len(s1) + 1)
    spinner = Spinner(len(s2))
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(
                    1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
        spinner.tick()
    spinner.finish()
    return distances[-1]


def levenshtein_distance_np(s1: str, s2: str) -> int:
    """
    Function calculate Levenshtein distance between two strings.

    Parameters
    s1 : str
        First string.
    s2 : str
        Second string.

    Returns
    int
        Levenshtein distance.
    """
    # I wanted to use numpy, but it's significantly slower than the plain python
    # version (tested with time() function).
    raise DeprecationWarning(
        "This function is deprecated. Use levenshtein_distance instead.")
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = np.arange(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = np.array([i2+1])
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_ = np.append(distances_, distances[i1])
            else:
                distances_ = np.append(
                    distances_, 1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def compare(file1: str, file2: str) -> float:
    """
    Function compare two files and return the normalized Levenshtein distance between them.

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
    with open(file2, "r", encoding="utf-8") as file:
        text2 = file.read()
    distance = levenshtein_distance(text1, text2) / max(len(text1), len(text2))
    return round(distance, 3)


def main(input_file: str, output_file: str) -> None:
    """
    Function compare all pairs of files from input_file and write the results to output_file.

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
            file1, file2 = line.split()
            distance = compare(file1, file2)
        except ValueError:
            logging.error(f"Incorrect line: {line}")
            distance = -1.0
        except FileNotFoundError:
            logging.error(f"One of files not found: {line}")
            distance = -1.0
        logging.info(f"Distance: {distance}")
        results.append(distance)
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(map(str, results)))
    logging.info(f"Successfully saved {len(results)} results to {output_file}")
    logging.info(f"Total time elapsed: {round(time.time() - start, 2)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to the input file.", type=str)
    parser.add_argument("output_file", help="Path to the output file.", type=str)
    args = parser.parse_args()
    main(args.input_file, args.output_file)
    # main("input.txt", "output.txt")
