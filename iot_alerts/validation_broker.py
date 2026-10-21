"""Optional local test broker adapter; not the deployed Mosquitto service."""
import argparse
import asyncio
import logging
import signal


async def serve(port):
    from amqtt.broker import Broker
    logging.basicConfig(level=logging.ERROR)
    broker = Broker({'listeners': {'default': {'type': 'tcp', 'bind': f'127.0.0.1:{port}'}},
                     'plugins': {'amqtt.plugins.authentication.AnonymousAuthPlugin': {'allow_anonymous': True}}})
    stop = asyncio.Event()
    for signum in (signal.SIGTERM, signal.SIGINT):
        asyncio.get_running_loop().add_signal_handler(signum, stop.set)
    await broker.start()
    try:
        await stop.wait()
    finally:
        await broker.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, required=True)
    args = parser.parse_args()
    asyncio.run(serve(args.port))
