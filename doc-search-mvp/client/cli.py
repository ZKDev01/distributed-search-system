import argparse
import requests


def main():
    parser = argparse.ArgumentParser(description="Doc Search CLI (MVP)")
    parser.add_argument(
        "--server", default="http://localhost:8000", help="URL del servidor FastAPI"
    )
    parser.add_argument("command", choices=["health"], help="Comando a ejecutar")
    args = parser.parse_args()

    if args.command == "health":
        r = requests.get(f"{args.server}/health", timeout=5)
        print(r.json())


if __name__ == "__main__":
    main()
