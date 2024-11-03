import argparse

from tools.cli_interface import CLIInterface


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--api_route",
        type=str,
        help="The local route to the flask API",
        default="http://localhost:8080",
    )

    args = parser.parse_args()

    interface = CLIInterface(api_route=args.api_route)

    interface()


if __name__ == "__main__":
    main()
