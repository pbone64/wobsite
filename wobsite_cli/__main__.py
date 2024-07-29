# import sys
# from os import path

# from argparse import ArgumentParser

# sys.path.append(path.join(path.dirname(__file__), path.pardir))

# from wobsite import Wobsite

# parser = ArgumentParser(
#     description="A dumb static site generator"
# )

# parser.add_argument(
#     "directory",
#     help="The website directory (folder containing wobsite.toml)"
# )

# args = parser.parse_args()

# directory = args.directory

# if not path.exists(directory):
#     print(f"{directory} does not exist")

# directory = path.realpath(directory)

# if not path.isdir(directory):
#     print(f"{directory} is not a directory")

# Wobsite(directory).compile()
