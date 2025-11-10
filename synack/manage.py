#!/usr/bin/env python3
"""
SYNOP (FM-12) Message Parser CLI

A command-line interface for parsing and analyzing SYNOP weather messages.
"""

import argparse
import sys
import json
import os
from pathlib import Path
from typing import List, Optional, TextIO
import csv

try:
    import yaml  # pip install PyYAML
except ImportError:
    yaml = None

# Import your parser module
from synack.parser import SYNOPParser, __version__


def setup_parser():
    """Set up the argument parser with all commands and options."""
    parser = argparse.ArgumentParser(
        description="SYNOP (FM-12) Message Parser CLI",
        epilog="""
Examples:
  # Parse a single message
  synop parse "AAXX 12345 12345 12345 12345"
  
  # Parse messages from a file
  synop parse -f messages.txt
  
  # Batch process multiple files
  synop batch-process ./data/ --output results.json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="Available commands",
        help="Additional help with <command> -h",
    )

    # Parser command
    setup_parse_command(subparsers)

    # Batch process command
    setup_batch_command(subparsers)

    return parser


def setup_parse_command(subparsers):
    """Set up the parse command for individual message parsing."""
    parser_parse = subparsers.add_parser(
        "parse",
        help="Parse individual SYNOP messages",
        description="Parse one or more SYNOP messages from command line or file",
    )

    # Input source group (mutually exclusive)
    input_group = parser_parse.add_argument_group()
    input_group.add_argument(
        "message", nargs="*", help="SYNOP message(s) to parse", metavar="MESSAGE"
    )
    input_group.add_argument(
        "-f",
        "--file",
        help="File containing SYNOP messages (one per line)",
        metavar="FILE",
    )
    input_group.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Interactive mode for entering messages",
    )

    # Output options
    output_group = parser_parse.add_argument_group("output options")
    output_group.add_argument(
        "-o", "--output", help="Output file (default: stdout)", metavar="FILE"
    )
    output_group.add_argument(
        "-F",
        "--format",
        choices=["json", "yaml", "csv", "table"],
        default="json",
        help="Output format (default: json)",
    )
    output_group.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output"
    )

    # Parsing options
    parse_group = parser_parse.add_argument_group("parsing options")
    parse_group.add_argument(
        "--strict", action="store_true", help="Enable strict parsing (fail on errors)"
    )
    parse_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output including warnings",
    )


def setup_batch_command(subparsers):
    """Set up the batch-process command for multiple files."""
    parser_batch = subparsers.add_parser(
        "batch-process",
        help="Process multiple SYNOP message files",
        description="Batch process multiple files or directories containing SYNOP messages",
    )

    parser_batch.add_argument(
        "input", help="Input file, directory, or glob pattern", metavar="INPUT"
    )

    parser_batch.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output file or directory",
        metavar="OUTPUT",
    )

    parser_batch.add_argument(
        "-F",
        "--format",
        choices=["json", "jsonl", "csv", "yaml"],
        default="json",
        help="Output format (default: json)",
    )

    parser_batch.add_argument(
        "--recursive", "-r", action="store_true", help="Process directories recursively"
    )

    parser_batch.add_argument(
        "--pattern", default="*.txt", help="File pattern to match (default: *.txt)"
    )

    parser_batch.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue processing even if some files fail",
    )


# Command implementations
def handle_parse_command(args):
    """Handle the parse command."""
    messages = []

    # Collect messages from different sources
    if args.message:
        messages = args.message
    elif args.file:
        with open(args.file, "r") as f:
            messages = [f.read()]
    elif args.interactive:
        messages = interactive_input()

    # Parse messages
    results = []
    errors = []

    parser = SYNOPParser()

    for i, message in enumerate(messages):
        try:
            result = parser.parse(message)
        except Exception as e:
            result = {
                "message": message,
                "parsed": "",
                "errors": [str(e)],
            }
        if result["errors"]:
            if args.strict:
                print(f"Error parsing message {i+1}: {e}", file=sys.stderr)
                sys.exit(1)
            else:
                errors.extend(result["errors"])
                if args.verbose:
                    print(
                        f"Warning: Failed to parse message {i+1}: {e}", file=sys.stderr
                    )
        results.append(result)

    # Output results
    output_file = open(args.output, "w") if args.output else sys.stdout

    try:
        if args.format == "json":
            output_data = {
                "results": results,
                "summary": {
                    "total": len(results),
                    "successful": len([r for r in results if not r["errors"]]),
                    "errors": len(errors),
                },
            }
            indent = 2 if args.pretty else None
            json.dump(output_data, output_file, indent=indent, ensure_ascii=False)

        elif args.format == "yaml":
            if yaml:
                yaml.dump(results, output_file, default_flow_style=False)
            else:
                print("yaml is not installed!")

        elif args.format == "csv":
            writer = csv.writer(output_file)
            writer.writerow(["Message", "Status", "Station_ID", "Error"])
            for result in results:
                station_id = (
                    result.get("parsed", {}).get("station_id", "")
                    if result["status"] == "success"
                    else ""
                )
                writer.writerow(
                    [
                        result["message"],
                        result["status"],
                        station_id,
                        result.get("error", ""),
                    ]
                )

        elif args.format == "table":
            print_table(results, output_file)

        if args.verbose and errors:
            print(
                f"\nSummary: {len(results) - len(errors)} successful, {len(errors)} errors",
                file=sys.stderr,
            )

    finally:
        if args.output:
            output_file.close()


def handle_batch_command(args):
    """Handle the batch-process command."""
    input_path = Path(args.input)
    output_path = Path(args.output)

    parser = SYNOPParser()

    # Find input files
    if input_path.is_file():
        files = [input_path]
    else:
        if args.recursive:
            files = list(input_path.rglob(args.pattern))
        else:
            files = list(input_path.glob(args.pattern))

    if not files:
        print(f"No files found matching pattern: {args.pattern}", file=sys.stderr)
        sys.exit(1)

    all_results = []

    for file_path in files:
        try:
            with open(file_path, "r") as f:
                messages = [line.strip() for line in f if line.strip()]

            file_results = []
            for message in messages:
                try:
                    result = parser.parse(message)
                    result["file"] = str(file_path)
                    file_result.append(result)
                except Exception as e:
                    file_results.append(
                        {
                            "file": str(file_path),
                            "message": message,
                            "error": str(e),
                        }
                    )

            all_results.extend(file_results)

        except Exception as e:
            if args.continue_on_error:
                print(f"Error processing {file_path}: {e}", file=sys.stderr)
                continue
            else:
                print(f"Error processing {file_path}: {e}", file=sys.stderr)
                sys.exit(1)

    # Write output
    if output_path.is_dir() or args.format in ["json", "jsonl"]:
        output_path.mkdir(parents=True, exist_ok=True)
        write_batch_output(all_results, output_path, args.format)
    else:
        write_batch_output(
            all_results, output_path.parent, args.format, output_path.name
        )


# Utility functions
def interactive_input() -> List[str]:
    """Collect messages interactively from user input."""
    print("Enter SYNOP messages (empty line to finish):")
    messages = []
    while True:
        try:
            line = input("> ").strip()
            if not line:
                break
            messages.append(line)
        except EOFError:
            break
    return messages


def print_table(results, output_file: TextIO):
    """Print results in a table format."""
    headers = ["#", "Status", "Station ID", "Message Preview"]
    rows = []

    for i, result in enumerate(results, 1):
        status = result["status"]
        station_id = (
            result.get("parsed", {}).get("station_id", "N/A")
            if status == "success"
            else "ERROR"
        )
        message_preview = (
            result["message"][:50] + "..."
            if len(result["message"]) > 50
            else result["message"]
        )

        rows.append([str(i), status, station_id, message_preview])

    # Simple table formatting
    col_widths = [
        max(len(str(row[i])) for row in [headers] + rows) for i in range(len(headers))
    ]

    # Header
    header_line = " | ".join(
        f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers))
    )
    separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    print(header_line, file=output_file)
    print(separator, file=output_file)

    for row in rows:
        row_line = " | ".join(f"{row[i]:<{col_widths[i]}}" for i in range(len(row)))
        print(row_line, file=output_file)


def write_batch_output(results, output_dir: Path, format: str, filename: str = None):
    """Write batch processing results in the specified format."""
    if format == "json":
        output_file = output_dir / (filename or "results.json")
        with open(output_file, "w") as f:
            json.dump(
                {
                    "results": results,
                    "summary": {
                        "total": len(results),
                        "successful": len(
                            [r for r in results if r["status"] == "success"]
                        ),
                        "errors": len([r for r in results if r["status"] == "error"]),
                    },
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

    elif format == "jsonl":
        output_file = output_dir / (filename or "results.jsonl")
        with open(output_file, "w") as f:
            for result in results:
                json.dump(result, f, ensure_ascii=False)
                f.write("\n")

    elif format == "csv":
        output_file = output_dir / (filename or "results.csv")
        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["File", "Status", "Station_ID", "Message", "Error"])
            for result in results:
                station_id = (
                    result.get("parsed", {}).get("station_id", "")
                    if result["status"] == "success"
                    else ""
                )
                writer.writerow(
                    [
                        result.get("file", ""),
                        result["status"],
                        station_id,
                        result["message"],
                        result.get("error", ""),
                    ]
                )

    print(f"Processed {len(results)} messages. Output: {output_file}")


def main():
    """Main CLI entry point."""
    parser = setup_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # Dispatch to appropriate command handler
        command_handlers = {
            "parse": handle_parse_command,
            "batch-process": handle_batch_command,
        }

        handler = command_handlers.get(args.command)
        if handler:
            handler(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose if hasattr(args, "verbose") else False:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
