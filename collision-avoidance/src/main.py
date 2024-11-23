from pathlib import Path

from src.cdm import parse_cdm


def main() -> None:
    cdm = parse_cdm(Path("data/CAESAR_TRJ_12.xml"))
    print(cdm)


if __name__ == "__main__":
    main()
