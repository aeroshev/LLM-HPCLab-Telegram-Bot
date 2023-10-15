import asyncio
import logging
import sys

from prometheus_client import start_http_server

from telegram.server import main

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    start_http_server(8000)
    asyncio.run(main())
