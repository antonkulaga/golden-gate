from pycomfort.files import *
from functional import seq
from typing import *
import typer
from pathlib import Path
from pycomfort.logging import to_nice_stdout, to_nice_file
import eliot
import dnacauldron as dc

app = typer.Typer()


def get_project_root() -> Path:
    """Find the project root by looking for pyproject.toml."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback to the parent of src if pyproject.toml not found
    return Path(__file__).parent.parent.parent


@app.command()
def process(
    assembly: Annotated[Path, typer.Option(help="Path to the assembly.csv file")] = None,
    plasmid: Annotated[List[Path], typer.Option(help="Path to the plasmids folder")] = None,
    logs: Annotated[Path, typer.Option(help="Path to the logs folder")] = None
    ) -> None:
    """
    Process golden gate assembly with the provided assembly.csv and plasmids folder.
    """
    project_root = get_project_root()
    input_folder = project_root / "data" / "input"
    output_folder = project_root / "data" / "output"
    
    if logs is None:
        logs = project_root / "logs"
    to_nice_stdout()
    to_nice_file(logs / "assembly.json", logs / "assembly.log")

    # Set defaults relative to project root
    if assembly is None:
        assembly = input_folder / "assembly.csv"
    
    if plasmid is None:
        plasmid = [input_folder]
    with eliot.start_action(action_type="process", include_args=True) as action:
        # Ensure logs directory exists
        logs.mkdir(exist_ok=True)
        
        action.log(f"Project root: {project_root}")
        action.log(f"Assembly CSV: {assembly}")
        action.log(f"Logs folder: {logs}")
        for plasmid_path in plasmid:
            action.log(f"Plasmids folder: {plasmid_path}")
            
        
        repository = dc.SequenceRepository()
        for plasmid_path in plasmid:
            # Get all files in the directory but exclude CSV files and other non-sequence files
            sequence_files = []
            if plasmid_path.is_dir():
                for file_path in plasmid_path.rglob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in ['.gb', '.gbk', '.fasta', '.fa', '.dna']:
                        sequence_files.append(str(file_path))
            
            if sequence_files:
                repository.import_records(files=sequence_files, use_file_names_as_ids=True, topology="circular")
            else:
                action.log(f"Warning: No sequence files found in {plasmid_path}")
        
        report_writer = dc.AssemblyReportWriter(include_mix_graphs=True, include_part_plots=True, include_fragment_plots=True, include_assembly_plots=True, include_pdf_report=True)

        # Verify that the assembly CSV file exists
        if not assembly.exists():
            action.log(f"Error: Assembly CSV file not found: {assembly}")
            raise typer.Exit(1)

        assembly_plan = dc.AssemblyPlan.from_spreadsheet(
            assembly_class=dc.Type2sRestrictionAssembly, path=str(assembly.absolute().resolve())
        )
        assembly_simulation = assembly_plan.simulate(sequence_repository=repository)
        df = assembly_simulation.compute_summary_dataframe()
        action.log(df)
        action.log(f"Assembly stats: {assembly_simulation.compute_stats()}")
        action.log("Assembly simulation results:")

        for s in assembly_simulation.assembly_simulations:
            action.log(f"{s.assembly.name}, errors: {s.errors}")

        action.log("Processing golden gate assembly...")
        assembly_simulation.write_report(str(output_folder / "assemblies"), assembly_report_writer=report_writer)



if __name__ == "__main__":
    app()