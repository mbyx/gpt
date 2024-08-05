import os
import subprocess

import dotenv
import google.generativeai as genai
import rich
import typer
from rich.console import Console

# Suppress logging warnings.
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

PROMPT: str = """You are a command line program.
- Given a task, you must write a series of commands to perform it.
- There must be exactly one command per line.
- The syntax of these commands must follow bash shell syntax.
- Do not add any decorations such as ```.
- When input does not conform to your guidelines, give your error or response in the form of a command.
- All output must be in the form of a command, even if you must echo it out."""

app = typer.Typer()
console = Console()

# TODO:
# - Persistent and permanent shell access.
# - Live streaming of stdout, so that long running tasks don't show their output only at the end.
# - Self prompting to gain new information about environment.
# - Better and more restrictive prompt.


@app.command()
def main(task: str, logging: bool = False) -> None:
    logging and console.log("[bold magenta]Loading[/bold magenta] Gemini API Key...")
    dotenv.load_dotenv()

    logging and console.log("[bold magenta]Creating[/bold magenta] Gemini model...")
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=PROMPT)

    logging and console.log(
        "[bold magenta]Starting[/bold magenta] chat with system prompt..."
    )
    chat = model.start_chat()

    try:
        logging and console.log(
            "[bold magenta]Sending[/bold magenta] task to Gemini..."
        )
        response = chat.send_message(task)
        for message in response.text.splitlines():
            rich.print(f"[bold]Command[/bold]: {message.strip()}")
            result = subprocess.run(message, capture_output=True, shell=True)
            rich.print(f"[bold]Output[/bold]: {result.stdout.decode()}")
    except genai.types.StopCandidateException:
        console.log("[bold red]ERROR[/bold red]: Specified task deemed dangerous.")
    except ValueError:
        console.log("[bold red]ERROR[/bold red]: No task specified.")


if __name__ == "__main__":
    app()
