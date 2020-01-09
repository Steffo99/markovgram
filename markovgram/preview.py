from typing import *
import click
import markovify


@click.command()
@click.argument("file", type=click.File("r", encoding="utf8"))
@click.option("-n", "--number", type=int, help="The number of sentences to generate.", default=100)
def run(file, number: int):
    text = markovify.NewlineText.from_json(file.read())
    file.close()
    for n in range(number):
        click.echo(text.make_sentence())


if __name__ == "__main__":
    run()
