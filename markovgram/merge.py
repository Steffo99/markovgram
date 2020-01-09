from typing import *
import click
import markovify


@click.command()
@click.option("-o", "--output-file", type=click.File("w", encoding="utf8"))
@click.argument("files", type=click.Path(exists=True, dir_okay=False), nargs=-1)
def run(output_file, files):
    texts = []
    for file in files:
        with open(file) as f:
            texts.append(markovify.NewlineText.from_json(f.read()))
    result = markovify.combine(texts)
    output_file.write(result.to_json())


if __name__ == "__main__":
    run()
