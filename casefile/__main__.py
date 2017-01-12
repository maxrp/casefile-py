from .config import read_config
from .casefile import new_case

if __name__ == "__main__":
    config = read_config()
    new_case(config['casefile'])
