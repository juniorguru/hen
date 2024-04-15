# Hen 🐔
Automated GitHub profile review.

## Installation

If you want to only use `hen` as a command line tool, install it using [pipx](https://pipx.pypa.io/):

```
pipx install 'git+https://github.com/juniorguru/hen.git'
```

If you later want to install updates:

```
pipx upgrade jg.hen
```

## Usage

The following checks given GitHub profile and prints a JSON with results:

```
hen https://github.com/PavlaBerankova
```

The result can be redirected to a file, which you can further process as you wish:

```
hen https://github.com/PavlaBerankova > report.json
```

## Development

Installation:

1.  You'll need [poetry](https://python-poetry.org/) installed.
2.  Clone this repository: `git clone git@github.com:juniorguru/hen.git`
3.  Go to the project directory: `cd hen`
4.  Install the project: `poetry install`

Running locally:

-   Set the `GITHUB_API_KEY` environment variable to your GitHub API token if you want higher GitHub API rate limits.
    Using [direnv](https://direnv.net/) might help setting environment variables automatically in your shell when you navigate to the project directory.
-   Run `poetry run hen --help` to start the program.

Useful commands:

-   To test, run `pytest`.
-   To format code, run `ruff format`.
-   To organize imports and fix other issues, run `ruff check --fix`.

## Name
Why Hen?
Because hens are mothers, they lovingly raise chicks.
This tool lovingly raises well-prepared juniors.

## License
Copyright (c) 2024 Jan Javorek, and contributors.
Unlike other junior.guru projects, this project uses [AGPL-3.0](LICENSE).
