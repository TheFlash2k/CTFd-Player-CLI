#!/usr/bin/env python3

import argparse
import argcomplete
import os
import tabulate
from .utils import *

def do_checks(args: argparse.Namespace, _config: dict, check_token: bool = False, check_challenges: bool = False):

    global config
    config = get_config(_config)
    
    if not hasattr(args, "url"): setattr(args, "url", "")

    if not config and not args.url:
        logger.error("Configuration file not found. Please run `ctfd init` to generate it first or specify url with --url")
        exit(1)
    
    args.url = args.url if args.url else config["CTFD"].get("URL", "")

    if not args.url:
        logger.error("No URL specified. Please check configuration or --url.")
        exit(1)

    args.token = config["CTFD"]["TOKEN"]

    if check_token:
        if not args.token:
            logger.error("No token found in the configuration file. Please run `ctfd generate-token` to generate a token.")
            exit(1)

    if check_challenges:
        if not config.get("Challenges", ""):
            logger.error("No challenges found. Please run `ctfd sync` to fetch the challenges from CTFd.")
            exit(1)

def check_downloaded_challenges(_chals: dict, chals_folder: str):
    """
    Check if the challenges are already downloaded. If they are, we'll update the attribute `is_downloaded` to True
    for the challenges that are already downloaded.
    """
    
    if not os.path.exists(chals_folder):
        return
    
    for i in range(len(_chals)):
        challenge = _chals[i]
        # Based on the category:
        category_folder = os.path.join(chals_folder, challenge["category"])
        if not os.path.exists(category_folder):
            continue

        _name = challenge['name'].replace(" ", "-").lower()
        chal_info = os.path.join(category_folder, f"{_name}/README.md")
        if os.path.exists(chal_info):
            challenge["is_downloaded"] = True

def _get_path() -> str:
    _path = os.path.join(os.getcwd(), ".ctfd")
    if not os.path.exists(_path):
        if os.path.exists("/tmp/.ctfd.cache"):
            with open("/tmp/.ctfd.cache") as fp:
                _path = fp.read().strip()
        else:
            return None
        
    return os.path.join(_path, "config.json")

def get_challenges(attr: str = "name"):

    if not (_path := _get_path()):
        return None
    _config = get_config(_path)

    challenges = _config.get("Challenges", None)
    if not challenges: return None
    return list(set([chal[attr] for chal in challenges]))

def get_container_challenges(attr: str = "name"):

    if not (_path := _get_path()):
        return None
    
    _config = get_config(_path)
    challenges = _config.get("Challenges", None)
    if not challenges: return None
    return [chal[attr] for chal in challenges if chal["type"] == "container"]

def main():
    parser = argparse.ArgumentParser(description='CTFd CLI for CTF Players to automate their workflows.')
    parser.add_argument('--config-dir', '-c', type=str, help='The directory where the configuration will be stored', default='.ctfd', dest='config_dir')
    parser.add_argument('--dir-name', '-d', type=str, help='Name of the folder', default="challenges", dest='chals_folder')
    parser.add_argument('--skip', '-s', action='store_true', help='Skip checking connection to CTFd instance', default=False, dest='skip')

    # Default args
    subparsers = parser.add_subparsers(title='Mode to operate the CLI in', dest='mode')
    
    # Subparser for setting up the CTF folder structure
    setup_parser = subparsers.add_parser('init', help="Setup the CTFd folder")
    setup_parser.add_argument('--token', '-t', type=str, help='CTFd Token', default=None)
    setup_parser.add_argument('--no-token', '-n', action='store_true', help='Do not prompt user for token', default=False)
    setup_parser.add_argument('--url', '-u', type=str, help='CTFd instance URL', default=None)
    setup_parser.add_argument('--force', '-f', action='store_true',help='Overwrite config file if it already exists', default=False)

    # Subparser for generating a token:
    generator_parser = subparsers.add_parser('generate-token', help="Generate a token by logging in as the user")
    generator_parser.add_argument('--url', '-u', type=str, help='CTFd instance URL', default=None)
    generator_parser.add_argument('--name', '-n', type=str, help='Username or email for login', required=True)
    generator_parser.add_argument('--password', '-p', type=str, help='Password for CTFd user')
    generator_parser.add_argument('--force', '-f', action='store_true',help='Overwrite token if already exists in the config file.', default=False)

    # Subparser for sync
    sync_parser = subparsers.add_parser('sync', help="Sync the challenges with the CTFd instance")
    sync_parser.add_argument('--force', '-f', action='store_true',help='Overwrite challenges if already exists in the config file.', default=False)

    # Subparser to download all the challenges
    challs_parser = subparsers.add_parser('challenges', help="Download challenges currently in CTFd")
    challs_parser.add_argument('--category', '-c', type=str, help="Download challenges of a specific category", default=None, choices=get_challenges("category"))
    challs_parser.add_argument('--name', '-n', type=str, help="Download a specific challenge", default=None, choices=get_challenges("name"))
    challs_parser.add_argument('--force', '-f', action='store_true',help='Overwrite challenges download files if already downloaded', default=False)

    # Subparser for flag submission
    submit_parser = subparsers.add_parser('submit', help="Submit flags for the challenges in CTFd")
    submit_parser.add_argument('--challenge-id', '-i', type=int, help="Challenge ID", default=None, dest='chal_id', choices=get_challenges("id"))
    submit_parser.add_argument('--challenge-name', '-n', type=str, help="Challenge Name (We'll fetch the challenge-id for you)", default=None, dest='chal_name', choices=get_challenges("name"))
    submit_parser.add_argument('--flag', '-f', type=str, help="The flag that you want to submit for the challenge.", default=None)

    # Subparser for instancer
    instance_parser = subparsers.add_parser('instance', help="Start an instance for a specific challenge in CTFd")
    instance_parser.add_argument('instance_mode', type=str, help="Start, stop or extend the instance", choices=["start", "stop", "extend"])
    instance_parser.add_argument('--challenge-id', '-i', type=int, help="Challenge ID", default=None, dest='chal_id', choices=get_container_challenges("id"))
    instance_parser.add_argument('--challenge-name', '-n', type=str, help="Challenge Name (We'll fetch the challenge-id for you)", default=None, dest='chal_name', choices=get_container_challenges("name"))

    # Subparser for scoreboard:
    scoreboard_parser = subparsers.add_parser('scoreboard', help="Get the scoreboard for the CTFd instance")
    scoreboard_parser.add_argument('-n', '--number', type=int, help="Number of top teams to display", default=10)

    # Solves subparser
    solves_parser = subparsers.add_parser('solves', help="Get the solves of a specific challenge")
    solves_parser.add_argument('--challenge-id', '-i', type=int, help="Challenge ID", default=None, dest='chal_id', choices=get_challenges("id"))
    solves_parser.add_argument('--challenge-name', '-n', type=str, help="Challenge Name (We'll fetch the challenge-id for you)", default=None, dest='chal_name', choices=get_challenges("name"))

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    # default config
    chals_folder = args.chals_folder
    args.config_dir = os.path.abspath(os.path.join(chals_folder, args.config_dir))

    if os.path.exists("/tmp/.ctfd.cache"):
        logger.warning("Using the cached configuration file path.")

    # store the updated config file path in /tmp/.ctfd.cache
    if not os.path.exists("/tmp/.ctfd.cache"):
        with open("/tmp/.ctfd.cache", "w") as fp:
            fp.write(f"{args.config_dir}")
    else:
        with open("/tmp/.ctfd.cache") as fp:
            args.config_dir = fp.read().strip()

    _config = os.path.join(args.config_dir, "config.json")
    # Bad coding. Don't do it like this. but works.
    args.chals_folder = chals_folder = os.path.abspath(os.path.join(args.config_dir, os.pardir))

    if args.mode == "init":

        if not args.url:
            args.url = input("Enter the CTFd URL: ")

        if not args.token and not args.no_token:
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
        do_checks(args, _config)

        if args.token and not args.force:
            logger.error("Token already exists in the configuration file. Please specify --force to overwrite it.")
            exit(1)

        generator = GenerateToken(args.url, args.name, args.password)
        args.token = generator.generate_token()

        write_config("CTFD", {"URL": args.url, "TOKEN": args.token}, _config)
        logger.info(f"Successfully generated token and written to {_config}")

    elif args.mode == "sync":

        """
        Sync will fetch all the existing challenges from the CTFd instance and write it to the configuration file.
        """
        do_checks(args, _config, check_token=True)

        if config.get("Challenges", "") and not args.force:
            logger.error("Challenges already exist in the configuration file. Please specify --force to refetch and update it.")
            exit(1)

        ctfd = CTFd_Handler(args.url, args.token, args.skip)
        logger.info("Fetching all the challenges deployed on CTFd")
        challenges = ctfd.get_challenges()
        
        _chals = []
        for challenge in challenges:
            chal = ChallengeModel(**challenge)
            logger.info(f"Found {chal} of category {chal.category}")
            _chals.append(chal.__dict__())
        
        check_downloaded_challenges(_chals, chals_folder)

        write_config("Challenges", _chals, _config, mode="a")

    elif args.mode == "challenges":
        """
        Idea for future reference:

        We will also copy ./templates/submit.sh and ./templates/launch.sh in each folder that, once invoked with flag as $1, will auto submit
        the flag because it will already contain the challenge-id and launch an instance of the challenge (if there is), respectively.
        """
        do_checks(args, _config, check_token=True, check_challenges=True)

        if args.category:
            challenges = config["Challenges"]
            challenges = [chal for chal in challenges if chal["category"] == args.category]

            if not challenges:
                logger.error(f"No challenges found for category {args.category}")
                exit(1)

        if args.name:
            challenges = config["Challenges"]
            challenges = [chal for chal in challenges if chal["name"] == args.name]

            if not challenges:
                logger.error(f"No challenges found for name {args.name}")
                exit(1)
                
        if not args.category and not args.name:
            challenges = config["Challenges"]

        if not challenges:
            logger.error("No challenges found. Please run `ctfd sync` to fetch the challenges from CTFd.")
            exit(1)

        ctfd = CTFd_Handler(args.url, args.token, args.skip)

        for challenge in challenges:
            chal = ChallengeModel(**challenge)

            if chal.is_downloaded and not args.force:
                logger.warning(f"Challenge {chal.name} is already downloaded, use --force to redownload.")
                continue

            logger.warning(f"Redownloading {chal.name}") if args.force else logger.info(f"Downloading {chal}")
            _chal = ctfd.get_challenge(chal.id)

            if not _chal:
                logger.error(f"Could not download {_chal}")
                continue

            category_folder = os.path.join(chals_folder, _chal["category"])
            os.makedirs(category_folder, exist_ok=True)

            chal_folder = os.path.join(category_folder, _chal['name'].replace(" ", "-"))
            os.makedirs(chal_folder, exist_ok=True)
            chal_info = os.path.join(chal_folder, "README.md")

            _files = []
            if files := _chal.get("files", []):
                for file in files:
                    filename = os.path.basename(file).split("?")[0]
                    logger.info(f"Downloading challenge file: {filename} for {_chal['name']}")

                    file_path = os.path.join(chal_folder, filename)
                    ctfd.download_file(file, file_path)
                    _files.append(file_path)

            with open(chal_info, "w") as fp:
                fp.write(f"# {_chal['name']}\n\n")
                fp.write(f"**Category**: {_chal.get('category', '')}\n")
                fp.write(f"**Points**: {_chal.get('value', '')}\n")
                fp.write(f"**Description**:\n```md\n{_chal.get('description', '')}\n```\n")
                if _files:
                    fp.write(f"**Files**:\n")
                    for file in _files:
                        fp.write(f"- [{os.path.basename(file)}]({file})\n")
            
            update_challenge(_config, chal.id, "is_downloaded", True)
            logger.info(f"Successfully downloaded {chal.name}")

            submit_sh_template = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates/submit.sh")

            update_template(submit_sh_template, os.path.join(chal_folder, "submit.sh"), chal.id, args.config_dir)

            if chal.type == "container":
                launch_sh_template = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates/launch.sh")
                update_template(launch_sh_template, os.path.join(chal_folder, "launch.sh"), chal.id, args.config_dir)

            logger.info(f"Successfully copied submit.sh {'and launch.sh' if chal.type == 'container' else ''} to {chal_folder}")

        logger.info("All challenges downloaded successfully.")

    elif args.mode == "submit":
        do_checks(args, _config, check_token=True)

        if not args.chal_id and not args.chal_name:
            logger.error("Please specify either challenge ID or challenge Name")
            exit(1)

        if not args.flag:
            args.flag = input("Enter the flag: ")

            if not args.flag:
                logger.error("No flag provided. Please specify the flag.")
                exit(1)

        if args.chal_name:
            challenges = config["Challenges"]
            chal = None
            for challenge in challenges:
                if challenge["name"] == args.chal_name:
                    chal = ChallengeModel(**challenge)
                    break

            if not chal:
                logger.error(f"No challenge found for name {args.chal_name}")
                exit(1)

            args.chal_id = chal.id

        if args.chal_id:
            challenges = config["Challenges"]
            chal = None
            for challenge in challenges:
                if challenge["id"] == args.chal_id:
                    chal = ChallengeModel(**challenge)
                    break

            if not chal:
                logger.error(f"No challenge found for ID {args.chal_id}")
                exit(1)

        ctfd = CTFd_Handler(args.url, args.token, args.skip)
        logger.info(f"Submitting flag for {chal}")

        resp = ctfd.submit_flag(chal.id, args.flag)
        if resp["status"] == "incorrect":
            logger.error("Incorrect Flag. Try again.")
            exit(1)

        elif resp["status"] == "correct":
            logger.info("🎉🎉🎉 Flag submitted successfully 🎉🎉🎉")

            if chal.type == "container":
                logger.info("Stopping instance for the challenge.")
                if resp := ctfd.stop_instance(chal.id):
                    if _err := resp.get('error', ''):
                        logger.error(f"Error: {_err}")
                        exit(1)
                    logger.info("Instance stopped successfully.")

        elif resp["status"] == "already_solved":
            logger.warning("🔒🔒🔒 Challenge already solved by your team 🔒🔒🔒")

        else:
            logger.error(f"Flag submission failed. Reason: {resp['message']}")

    elif args.mode == "instance":
        do_checks(args, _config, check_token=True)
        
        if not args.chal_id and not args.chal_name:
            logger.error("Please specify either challenge ID or challenge Name")
            exit(1)

        if args.chal_name:
            challenges = config["Challenges"]
            chal = None
            for challenge in challenges:
                if challenge["name"] == args.chal_name:
                    chal = ChallengeModel(**challenge)
                    break

            if not chal:
                logger.error(f"No challenge found for name {args.chal_name}")
                exit(1)

            args.chal_id = chal.id

        if args.chal_id:
            challenges = config["Challenges"]
            chal = None
            for challenge in challenges:
                if challenge["id"] == args.chal_id:
                    chal = ChallengeModel(**challenge)
                    break

            if not chal:
                logger.error(f"No challenge found for ID {args.chal_id}")
                exit(1)

        if chal.type != "container":
            logger.error(f"Challenge {chal.name} is not a container challenge.")
            exit(1)
        
        ctfd = CTFd_Handler(args.url, args.token, args.skip)

        if args.instance_mode == "start":

            logger.info(f"Starting instance for {chal}")
            resp = ctfd.start_instance(chal.id)
            if not resp:
                logger.error(f"Failed to start instance for {chal.name}")
                exit(1)

            if _err := resp.get('error', ''):
                logger.error(f"Error: {_err}")
                if "Please stop" in _err:
                    logger.error("Use `ctfd instance stop` command to stop the instance.")
                exit(1)

            if resp["status"] == "already_running":
                logger.warning("Instance already running for this challenge.")

            _i = f"http://{resp['hostname']}:{resp['port']}" if resp['connect'] == "http" else f"nc {resp['hostname']} {resp['port']}"
            logger.info(f"Connect: \033[91m\033[4m\033[1m{_i}\033[0m")

        elif args.instance_mode == "extend":
            logger.info(f"Extending instance time for {chal}")
            resp = ctfd.extend_instance(chal.id)
            if not resp:
                logger.error(f"Failed to extend instance for {chal.name}")
                exit(1)

            if _err := resp.get('error', ''):
                logger.error(f"Error: {_err}")
                exit(1)

            logger.info("Instance extended successfully.")
            _i = f"http://{resp['hostname']}:{resp['port']}" if resp['connect'] == "http" else f"nc {resp['hostname']} {resp['port']}"
            logger.info(f"Connect: \033[91m\033[4m\033[1m{_i}\033[0m")

        elif args.instance_mode == "stop":
            logger.info(f"Stopping instance for {chal}")
            resp = ctfd.stop_instance(chal.id)
            if not resp:
                logger.error(f"Failed to stop instance for {chal.name}")
                exit(1)

            if _err := resp.get('error', ''):
                logger.error(f"Error: {_err}")
                exit(1)
            
            if msg := resp.get("success", ""):
                logger.info("Instance stopped successfully.")

    elif args.mode == "scoreboard":
        do_checks(args, _config)

        ctfd = CTFd_Handler(args.url, args.token, args.skip)
        logger.info(f"Getting scoreboard for the CTFd instance")

        scoreboard = ctfd.get_scoreboard(args.number)
        if not scoreboard:
            logger.error("No scoreboard found.")
            exit(1)

        headers = ["Rank", "Team", "Score"]
        table = []

        for pos, team in scoreboard.items():
            table.append([pos, team["name"], team["score"]])

        print(tabulate.tabulate(table[:args.number], headers, tablefmt="fancy_outline"))

    elif args.mode == "solves":
        do_checks(args, _config)

        if not args.chal_id and not args.chal_name:
            logger.error("Please specify either challenge ID or challenge Name")
            exit(1)

        if args.chal_name:
            challenges = config.get("Challenges", [])
            if not challenges:
                logger.error("No challenges found. Please run `ctfd sync` to fetch the challenges from CTFd.")
                exit(1)
            chal = None
            for challenge in challenges:
                if challenge["name"] == args.chal_name:
                    chal = ChallengeModel(**challenge)
                    break

            if not chal:
                logger.error(f"No challenge found for name {args.chal_name}")
                exit(1)

            args.chal_id = chal.id

        if args.chal_id:
            challenges = config.get("Challenges", [])
            if not challenges:
                logger.error("No challenges found. Please run `ctfd sync` to fetch the challenges from CTFd.")
                exit(1)
            chal = None
            for challenge in challenges:
                if challenge["id"] == args.chal_id:
                    chal = ChallengeModel(**challenge)
                    break

            if not chal:
                logger.error(f"No challenge found for ID {args.chal_id}")
                exit(1)

        ctfd = CTFd_Handler(args.url, args.token, args.skip)
        logger.info(f"Getting solves for {chal}")

        solves = ctfd.get_solves(chal.id)
        if not solves:
            logger.error(f"No solves found for {chal.name}")
            exit(1)

        headers = ["Name", "Date"]
        table = []

        for solve in solves:
            table.append([solve["name"], solve["date"]])

        print(tabulate.tabulate(table, headers, tablefmt="fancy_outline"))

    else:
        logger.error("Invalid mode specified.")
        parser.print_help()