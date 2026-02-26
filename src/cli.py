import argparse
import asyncio
from pathlib import Path
from src.main import run_workflow

def parse_args():
    parser = argparse.ArgumentParser(
        description="MathFormula2Tex CLI"
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=Path,
        help="输入图片目录",
    )

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=Path,
        help="输出 tex 目录",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    input_dir = args.input.resolve()
    output_dir = args.output.resolve()

    if not input_dir.exists():
        raise FileNotFoundError(f"输入目录不存在: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    asyncio.run(
        run_workflow(
            input_dir=input_dir,
            output_dir=output_dir,
        )
    )


if __name__ == "__main__":
    main()
