import argparse
from .server import server
from .options import configuration
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description="CMake Language Server")
    parser.add_argument(
        "--tcp", action="store_true", help="Use TCP server instead of Update stdio"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind to this address")
    parser.add_argument("--port", type=int, default=2087, help="Bind to this port")
    parser.add_argument("--enable-cmake-annotations", action="store_true", help="Load bundled CMake annotations")
    parser.add_argument("--expand-env-variable", action="store_true", help="Expand $ENV{NAME} using the server process environment")
    parser.add_argument("--annotation", action="append", default=[], metavar="PATH", help="Load an external annotation pack (repeatable, in order)")
    args = parser.parse_args(argv)
    server.annotation_defaults = configuration({"fleurdelys": {
        "enableCMakeAnnotations": args.enable_cmake_annotations,
        "additionalAnnotations": args.annotation,
        "expandEnvVariable": args.expand_env_variable,
    }}, base=Path.cwd())

    if args.tcp:
        server.start_tcp(args.host, args.port)
    else:
        server.start_io()


if __name__ == "__main__":
    main()
