# cpias

Cell Profiling Image Analysis Server

## Install

```sh
git clone https://github.com/CellProfiling/cpias.git
cd cpias
pip install .
```

## Run

- Open a terminal, we call it terminal 1. In terminal 1, start the server.

```sh
cpias --help
# Start the server
cpias start-server
```

- Open another terminal, we call it terminal 2. In terminal 2 run the client.

```sh
# Run the client
cpias run-client
```

## Add new commands

New commands should preferably be added in a standalone package, by using a `setup.py` file and the `entry_points` interface.
`cpias` will look for entry points registered under `"cpias.commands"`.

```py
# setup.py
...
entry_points={
    "cpias.commands": ["hello = cpias.commands.hello"],
},
...
```

See the [`setup.py`](setup.py) file of this package for a real example.
See the packaging [docs](https://packaging.python.org/guides/creating-and-discovering-plugins/#using-package-metadata) for details.

This will load all the command modules specified in the list, eg `cpias.commands.hello`.
Inside each module there should be a function defined named `register_command`. It should accept one positional argument, `server`.
This is the `cpias` server instance.

```py
def register_command(server: "CPIAServer") -> None:
    """Register the hello command."""
    server.register_command("hello", hello)
```

See the [`hello.py`](cpias/commands/hello.py) command included in this package for examples of different types of commands.

## Message structure

`cpias` uses a json serialized format for the messages sent over the socket.
Each message should contain three items in the json object, `cli`, `cmd` and `dta`.

- Here's an example message as json.

```json
{"cli": "client-1", "cmd": "hello", "dta": {"param1": "world"}}
```

- Here's the same message serialized and with line break to mark message end. It's the serialized version of the message that should be sent over the socket.

```py
'{"cli": "client-1", "cmd": "hello", "dta": {"planet": "world"}}\n'
```

- The `cli` item should mark the client id.
- The `cmd` item should mark the command id.
- The `dta` item should hold another json object with arbitrary data items. Only requirement is that the message can be serialized.
Each item in `dta` will be passed to the command function as a named argument.

## Development

```sh
pip install -r requirements_dev.txt
# Use the makefile for common dev tasks
make
```

- Here's a list of development tools we use.
  - black
  - flake8
  - pylint
  - pydocstyle
  - mypy
  - pytest
  - tox
