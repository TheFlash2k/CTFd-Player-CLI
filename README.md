# CTFd-CLI
A simple utility that allows interacting with CTFd easier, submitting flags, downloading challenges, all from the CLI. The only thing you'll need to do is generate a token, which you can even do by just providing your creds.

## Setup

To setup `ctfd`, just run the following command:

```bash
$ sudo python3 setup.py install
```

> **NOTE:** Atleast `Python 3.7` is required to run this utility.

## Usage

The usage is fairly is simple. Consider a scenario where you're playing a CTF. The first thing you'll do is create a folder, let's say, `ABC-CTF`. The next thing you'll need to do is run:

```bash
$ ctfd init [--url <URL>] [--token <TOKEN>]
```

> If no arguments are provided, you'll be prompted to manually enter those. You **CAN** skip entering token by just pressing enter.

Now, let's say you don't have a token, you can generate a token using `generate-token` command:

```bash
$ ctfd generate-token --name <username/email> --password <password>
```

What this will do is generate a token for you. There also is a parameter called `--force`, that'll be used in case you want to forcefully generate another token.

> The token and URL will be stored in `.ctfd/config.json`.

Once this is done, you need to get the list of all challenges, these challenges name and id will be stored inside the `.ctfd/config.json` file. The command used will be:

```bash
$ ctfd sync
```

After this, in order to fetch a challenge's attachments and details, you can use `challenges` command.

```bash
$ ctfd challenges [--category <category>] [--name <challenge-name>]
```

> **NOTE:** If no arguments are provided, it will download all the challenges, their attachments, hints, points and category and store in a directory structure like: `Challenges/<Category>/<Name>/README.md`

In case challenges have instances specifically [containers](https://github.com/theflash2k/containers) plugin, you can start, stop and extend as well.

```bash
# Atleast one must be provided.
$ ctfd instance start [--challenge-id <ID>] [--challenge-name <NAME>]

# To stop:
$ ctfd instance stop [--challenge-id <ID>] [--challenge-name <NAME>]

# To extend time:
$ ctfd instance extend [--challenge-id <ID>] [--challenge-name <NAME>]
```

You can also submit flags from the command-line:

```bash
$ ctfd submit --challenge-id <ID> --flag <FLAG>
```

For your ease, whenever you run: `ctfd challenges`, I will create two scripts in the challenge directory: `launch.sh` and `submit.sh`. `launch.sh` will only exist for challenges that have their type = container. But `submit.sh` will be there for all challenges. You can submit a challenge using `./submit.sh <flag>`. Whereas, `launch.sh` won't take any parameter and will just start the instance for that specific challenge.

You can also see the scoreboard and solves on a particular challenge:

```bash
$ ctfd scoreboard [-n <max-results> {Default: 10}]
# OR
$ ctfd solves [--challenge-id <ID>] [--challenge-name <NAME>]
```

## Autocompletions

Under the hood, this tool utilizes `argcomplete` library for autocomplettions. To make it work, please firstly run this command:

```bash
$ activate-global-python-argcomplete
```

After this is done, add this to your `.zsh/.bashrc`

```bash
eval "$(register-python-argcomplete ctfd)"
```

Once this is done, you will tab autocompletion for your `ctfd` utility.


## Future Work

Extracting components from the other [CTFd CLI](https://github.com/TheFlash2k/CTFd-CLI) and then migrating the code to a single CLI application.
