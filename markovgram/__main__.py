from typing import *
import click
import markovify
import json
import os
import re


def underscorize(string: str) -> str:
    """Replace all non-word characters in a :class:`str` with underscores.
    It is particularly useful when you want to use random strings from the Internet as filenames.

    Parameters:
        string: the input string.

    Returns:
        The resulting string.
    Example:
        ::
            >>> underscorize("LE EPIC PRANK [GONE WRONG!?!?]")
            "LE EPIC PRANK _GONE WRONG_____"
    """
    return re.sub(r"\W", "_", string)


def render_element(element: Union[Dict[str, str], str]):
    if isinstance(element, str):
        return element
    elif isinstance(element, dict):
        return element.get("text", "")
    else:
        raise TypeError("Unknown element type")


def merge_message(message: Union[List[str], str]):
    if isinstance(message, str):
        return message
    elif isinstance(message, list):
        return "".join([render_element(element) for element in message])
    raise TypeError("Unknown message type")


def create_chats_newlinetext(chats: List[Dict[str, Any]], state_size) -> Optional[markovify.NewlineText]:
    # Create a list with all messages
    messages: List[List[str]] = []
    # For chat in the list
    for chat in chats:
        # Find the chat name
        name: str = chat.get("name")
        if name is None:
            name = "Unknown"
        # For update in the chat
        with click.progressbar(chat["messages"],
                               label=name,
                               length=len(chat["messages"]),
                               show_percent=True,
                               fill_char="█",
                               empty_char="░") as updates_bar:
            for update in updates_bar:
                # Check that the update is not a service update
                if update["type"] != "message":
                    continue
                # Check that the sender is not a bot (null?)
                if update.get("from") is None:
                    continue
                # Find the message inside the update
                message: str = merge_message(update["text"])
                # Skip commands
                if message.startswith("/"):
                    continue
                # Split the message in words
                words: List[str] = message.split()
                # Append the words to the messages
                messages.append(words)
    # If the chat has no messages, return None
    if len(messages) == 0:
        return None
    # Create the chain from the words
    chain = markovify.Chain(messages, state_size=state_size)
    # Return the chain
    text = markovify.NewlineText(None, state_size=state_size, chain=chain)
    # Return the text
    return text


def create_file(path, chats, state_size):
    text: markovify.NewlineText = create_chats_newlinetext(chats, state_size)
    if text is None:
        click.echo(f"{path}: Text generation failed", err=True)
        return
    with open(path, "w") as output_file:
        output_file.write(text.to_json())


@click.command()
@click.option("-d", "--data-folder", type=click.Path(exists=True, file_okay=False), prompt=True)
@click.option("-o", "--output-folder", type=click.Path(), default="markovgram_output")
@click.option("-s", "--state-size", type=int, prompt=True)
def main(data_folder, output_folder, state_size):
    result_path = os.path.join(data_folder, "result.json")
    try:
        os.mkdir(output_folder)
    except OSError:
        pass

    click.echo(f"Reading {result_path} ...")
    with open(result_path, encoding="utf8") as result_file:
        try:
            result = json.load(result_file)
        except json.decoder.JSONDecodeError:
            raise click.ClickException("result.json file is corrupt and can't be decoded.\n"
                                       "Did the data export finish correctly?")

    chats = [chat for chat in result["chats"]["list"]]

    click.echo("Creating by_chat texts:")
    by_chat_output_path = os.path.join(output_folder, "by_chat")
    try:
        os.mkdir(by_chat_output_path)
    except OSError:
        pass
    for chat in chats:
        name: str = chat.get("name")
        if name is None:
            name = "Unknown"
        chat_id: int = chat["id"]
        output_path = os.path.join(by_chat_output_path, f"{underscorize(name)}_{chat_id}.json")
        create_file(path=output_path, chats=[chat], state_size=state_size)

    click.echo("Creating everything text...")
    everything_output_path = os.path.join(output_folder, "everything.json")
    create_file(path=everything_output_path, chats=chats, state_size=state_size)


if __name__ == "__main__":
    main()
