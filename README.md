# Context Fuse

Context Fuse is a script that aggregates data into a unified context file to enhance AI prompting.

It clones a given Git repository, scrapes all text-based files, and produces a single output file with clear file delimiters.

## Setup

1. Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```

2. Activate the virtual environment:
    - On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script with a repository URL or website URL as an argument:

```bash
./context_fuse.py --git <repository_url>
```

or

```bash
./context_fuse.py --web <website_url>
```

## Development Setup

1. Install development dependencies:
    ```bash
    pip install -r dev-requirements.txt
    ```

2. Run the code formatters and linters:
    ```bash
    ./run_checks.sh
    ```
