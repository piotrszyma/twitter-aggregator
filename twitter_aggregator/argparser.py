import argparse
import dataclasses
from dacite.core import from_dict


@dataclasses.dataclass(frozen=True)
class CliArgs:
    config_path: str


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-path", type=str, required=True)
    args = parser.parse_args()
    return from_dict(data_class=CliArgs, data=vars(args))
