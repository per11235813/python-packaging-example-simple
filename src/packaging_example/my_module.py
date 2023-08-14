from importlib.resources import files
from pathlib import Path
import pandas as pd
import io


def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def hello():
    print("hello, world!"),

    print("\nData collected from the package with importlib.resources:")
    csv_path: Path = files("packaging_example.data") / "data.csv"
    csv_text = csv_path.read_text()
    df = pd.read_csv(io.StringIO(csv_text))
    print(df)


def hello2():
    print(f"hello, world! {fib(14)=}")


if __name__ == "__main__":
    hello()
