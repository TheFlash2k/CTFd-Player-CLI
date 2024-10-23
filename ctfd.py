#!/usr/bin/env python3

import argparse
import os

from utils import *
from generate import GenerateToken

"""
There are multiple ways we can go about this.
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Auto-CTFd CLI')

    # Default args
    subparsers = parser.add_subparsers(required=True, dest='mode')
    parser.add_argument('--config-dir', '-c', type=str, help='The directory where the configuration will be stored', default='.ctfd', dest='config_dir')
    
    # Subparser for setting up the CTF folder structure
    setup_parser = subparsers.add_parser('setup', help="Setup the CTFd folder")
    setup_parser.add_argument('--token', '-t', type=str, help='CTFd Token', default=None)
    setup_parser.add_argument('--url', '-u', type=str, help='CTFd instance URL', default=None)
    setup_parser.add_argument('--force', action='store_true',help='Overwrite config file if it already exists', default=False)

    # Subparser for generating a token:
    generator_parser = subparsers.add_parser('generate-token', help="Generate a token by logging in as the user")
    generator_parser.add_argument('--url', '-u', type=str, help='CTFd instance URL', default=None)
    generator_parser.add_argument('--name', type=str, help='Username or email for login', required=True)
    generator_parser.add_argument('--password', type=str, help='Password for CTFd user')
    generator_parser.add_argument('--force', action='store_true',help='Overwrite token if already exists in the config file.', default=False)
 
    args = parser.parse_args()

    # default config
    _config = os.path.join(args.config_dir, ".config")

    if args.mode == "setup":
        """
        
        """
        if not args.url:
            args.url = input("Enter the CTFd URL: ")

        if not args.token:
            args.token = input("Enter the CTFd token: ")
            if not args.token: # i mean, if it works, it works, right?
                logger.warning("No token has been provided, make sure you run `ctfd generate-token` with the appropriate credentails to generate a token.")

        if os.path.exists(_config) and not args.force:
            logger.error(f"Config file \"{_config}\" already exists. Please use --force to overwrite")
            exit(0)
        else:
            os.makedirs(args.config_dir, exist_ok=True) # create the .config folder.
            
        write_config("CTFD", {"URL": args.url, "TOKEN": args.token}, _config)
        logger.info(f"Successfully wrote configurations to: {_config}")

    elif args.mode == "generate-token":

        """
        We'll make a request to the /api/v1/tokens to generate a new token.

        But we'll manually login first, then using the CSRF-Token to interact
        with the API.
        """
        config = get_config(_config)

        if not config and not args.url:
            logger.error("Configuration file not found. Please run `ctfd setup` to generate it first or specify url with --url")
            exit(1)
        
        args.url = config["CTFD"]["URL"] if not args.url else args.url

        if not args.url:
            logger.error("No URL specified. Please check configuration or --url.")
            exit(1)

        args.token = config["CTFD"]["TOKEN"]
        if args.token and not args.force:
            logger.error("Token already exists in the configuration file. Please specify --force to overwrite it.")
            exit(1)

        generator = GenerateToken(args.url, args.name, args.password)
        args.token = generator.generate_token()

        write_config("CTFD", {"URL": args.url, "TOKEN": args.token}, _config)
        logger.info(f"Successfully generated token and written to {_config}")

    elif args.mode == "challenges":
        pass

    elif args.mode == "submit":
        pass