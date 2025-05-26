import tomli

def parse_toml(file):
    with open(file, "rb") as f:
        toml = tomli.load(f)
    return toml
