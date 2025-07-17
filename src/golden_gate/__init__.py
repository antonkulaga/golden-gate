from pycomfort.files import *
from functional import seq
from typing import *
import typer
from pathlib import Path

app = typer.Typer()


@app.command()
def process(
    assembly: Path = typer.Argument(..., help="Path to the assembly.csv file"),
    plasmids_folder: Path = typer.Option(
        Path("./data/plasmid"),
        "--plasmids-folder",
        "-p", 
        help="Path to the plasmids folder"
    )
) -> None:
    """
    Process golden gate assembly with the provided assembly.csv and plasmids folder.
    """
    typer.echo(f"Assembly CSV: {assembly}")
    typer.echo(f"Plasmids folder: {plasmids_folder}")
        
    import dnacauldron as dc
    repository = dc.SequenceRepository()
    #for plasmid in plasmids_folder.glob("*.fasta"):
    #repository.import_records(folder=str(locations.moclo_toolkit), use_file_names_as_ids=True, topology="circular")


    # Verify that the assembly CSV file exists
    if not assembly.exists():
        typer.echo(f"Error: Assembly CSV file not found: {assembly}", err=True)
        raise typer.Exit(1)
    
    # Verify that the plasmids folder exists
    if not plasmids_folder.exists():
        typer.echo(f"Error: Plasmids folder not found: {plasmids_folder}", err=True)
        raise typer.Exit(1)
    
    # TODO: Add your golden gate assembly processing logic here
    typer.echo("Processing golden gate assembly...")


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()