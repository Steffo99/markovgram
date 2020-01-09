from typing import *
import click
import markovify


@click.command()
@click.argument("files", type=click.Path(exists=True, dir_okay=False), nargs=-1)
@click.option("-o", "--output-file", type=click.File("w", encoding="utf8"))
def run(files: Tuple[str], output_file: str):
    texts = []
    with click.progressbar(files,
                           label="Opening files...",
                           length=len(files),
                           show_percent=True,
                           fill_char="█",
                           empty_char="░") as files_bar:
        for filename in files_bar:
            with open(filename) as file:
                text = markovify.NewlineText.from_json(file.read())
            texts.append(text)
    click.echo("Merging...")
    merged = markovify.combine(texts)
    click.echo("")
    with open(output_file, "w") as output_file:
        output_file.write(merged.to_json())


if __name__ == "__main__":
    run()
