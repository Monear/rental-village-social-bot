# Podman Commands for Rental Village Social Bot

This document outlines common Podman commands for building and running the Rental Village Social Bot.

## 1. Building the Image

To build the container image for the bot, navigate to the project root directory (where the `Dockerfile` is located) and run:

```bash
sudo podman build -t rental-village-bot .
```

This command builds an image named `rental-village-bot` from the current directory's `Dockerfile`.

## 2. Checking Notion Database Structure

To inspect the schema of your connected Notion database using `src/utils/check_notion_db.py`, run the following command. Ensure your `.env` file is correctly configured in the project root.

```bash
sudo podman run --rm --env-file .env rental-village-bot python src/utils/check_notion_db.py
```

*   `--rm`: Automatically removes the container when it exits.
*   `--env-file .env`: Mounts your `.env` file into the container, providing necessary environment variables (like API keys).
*   `rental-village-bot`: The name of the image you built.
*   `python src/utils/check_notion_db.py`: The command executed inside the container.

## 3. Running Other Scripts

You can run any other script within the container using a similar pattern. For example, to run `suggest_content.py`:

```bash
sudo podman run --rm --env-file .env rental-village-bot python src/suggest_content.py --num-ideas 2
```

Remember to replace `src/suggest_content.py --num-ideas 2` with the specific script and its arguments you wish to execute.

## 4. Running Tests

To run the comprehensive test suite within the container, first ensure your image is built with the latest code and dependencies. Then, execute:

```bash
sudo podman run --rm rental-village-bot pytest
```

This command will run all tests located in the `tests/` directory inside the `rental-village-bot` container.