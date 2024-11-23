from pathlib import Path

from src.cdm import parse_cdm


def main() -> None:
    cdm = parse_cdm(Path("data/CSPOC_9.xml"))
    print(cdm)


if __name__ == "__main__":
    main()
