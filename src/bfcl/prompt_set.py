import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from bfcl.constants.category_mappings import TestCollection

logger = logging.getLogger(__name__)


def build_prompt_dataset(categories: List[TestCollection]) -> List[Dict[str, Any]]:
    """
    Build a prompt dataset based on test categories.

    Args:
        categories: List of TestCollection categories to process

    Returns:
        List of prompt samples with metadata and content
    """
    prompt_dataset = []

    all_test_categories = []
    for category in categories:
        all_test_categories.extend(category.value[2])

    all_test_categories = list(set(all_test_categories))

    data_dir = Path(__file__).parent / "data"

    for test_category in all_test_categories:
        filename = test_category.value[2]
        file_path = data_dir / filename

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue

                    sample = json.loads(line)

                    prompt_sample = {"metainfo": {"id": sample["id"]}, "prompt": sample["question"][0]}

                    prompt_dataset.append(prompt_sample)

        except FileNotFoundError:
            logger.warning(f"Warning: File {file_path} not found. Skipping...")
        except json.JSONDecodeError:
            logger.warning(f"Warning: Error parsing JSON in {file_path}. Skipping...")
        except (KeyError, IndexError) as e:
            logger.warning(f"Warning: Error processing data in {file_path}: {e}. Skipping...")

    return prompt_dataset


def save_prompt_dataset(dataset: List[Dict[str, Any]], output_file: str) -> None:
    """
    Save the constructed prompt dataset to a JSON file.

    Args:
        dataset: The prompt dataset to save
        output_file: Path to the output file
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)


def main():
    """
    Main function to handle command line arguments and build the prompt dataset.
    """
    parser = argparse.ArgumentParser(description="Construct a prompt dataset from BFCL test categories")

    parser.add_argument(
        "--categories",
        nargs="+",
        choices=[category.name.lower() for category in TestCollection],
        required=True,
        help="Specify one or more TestCollection categories to process ('all', 'single_turn', 'live', 'non_live', 'executable', 'non_python', 'python', 'python_ast', 'irrelevance')",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="prompt_dataset.json",
        help="Path to save the output dataset (default: prompt_dataset.json)",
    )

    args = parser.parse_args()

    categories = []
    for category_name in args.categories:
        for category in TestCollection:
            if category.name.lower() == category_name.lower():
                categories.append(category)
                break

    if not categories:
        logger.error("Error: No valid categories specified.")
        return

    prompt_dataset = build_prompt_dataset(categories)

    save_prompt_dataset(prompt_dataset, args.output)

    logger.info(f"Successfully built prompt dataset with {len(prompt_dataset)} samples.")
    logger.info(f"Dataset saved to {args.output}")


if __name__ == "__main__":
    main()
