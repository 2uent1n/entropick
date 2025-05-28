# EntroPick

**Fair and random reviewer assignment for pull requests via Slack**

EntroPick is a Slack app built with the Bolt framework that allows fair and random selection of reviewers for your pull requests. Create customizable reviewer pools and ensure equitable distribution of code review tasks across your team or organization.

## Installation

### Prerequisites

- Python 3.13+
- uv package manager

### Setup

1. **Clone the project**

```bash
git clone git@github.com:2uent1n/entropick.git
cd entropick
```

2. **Create and setup virtual environment**

```bash
uv venv
source .venv/bin/activate
uv sync
```

3. **Run the application**

```bash
python main.py
```

## Development

### Code Quality

- **Linting**: `ruff check .`
- **Formatting**: `ruff format .`

### Project Structure

```
entropick/
├── main.py              # Application entry point
├── pyproject.toml       # Project configuration and dependencies
├── .python-version      # Python version
└── README.md            # Project documentation
```
