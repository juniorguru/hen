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

To check a GitHub profile and print JSON with results, run the following:

```
hen https://github.com/PavlaBerankova
```

The result can be redirected to a file, which you can further process as you wish.

```
hen https://github.com/PavlaBerankova > report.json
```

## Development

Installation:

1.  You'll need [uv](https://docs.astral.sh/uv/) installed.
2.  Clone this repository: `git clone git@github.com:juniorguru/hen.git`
3.  Go to the project directory: `cd hen`
4.  Install the project: `uv sync`

Running locally:

-   Set the `GITHUB_API_KEY` environment variable to your GitHub API token if you want higher GitHub API rate limits.
    Using [direnv](https://direnv.net/) might help setting environment variables automatically in your shell when you navigate to the project directory.
-   Run `uv run hen --help` to start the program.

Useful commands:

-   To test, run `uv run pytest`.
-   To format code, run `uv run ruff format`.
-   To organize imports and fix other issues, run `uv run ruff check --fix`.

## Getting raw data
Using `-r` records data from GitHub to the `.data` directory.
Such data is useful if you want to debug your rules or [test them against real world fixtures](https://github.com/yanyongyu/githubkit/issues/98#issuecomment-2059235461).

## Name
Why Hen?
Because hens are mothers, they lovingly raise chicks.
This tool lovingly raises well-prepared juniors.

## License
[AGPL-3.0-only](LICENSE), copyright (c) 2024 Jan Javorek, and contributors.
