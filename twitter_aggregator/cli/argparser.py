import argparse
import dataclasses


@dataclasses.dataclass
class CliArgs:
    config_path: str


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str)
    args = parser.parse_args()
    return CliArgs(config_path=args.config)
