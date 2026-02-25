from pathlib import Path
from typing import Dict
from src.llm.services.chapter_dispatcher import ChapterResult

class ChapterWriter:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_tex(self, chapter_result: Dict[str, ChapterResult], file_name: str = "output.tex"):
        output_file = self.output_dir / file_name
        with output_file.open('w', encoding='utf-8') as f:
            for title, result in chapter_result.items():
                if not result.success:
                    print(f"❌ {title} 写入失败: {result.error}")
                else:
                    print(f"✅ {title} 写入成功")
                    f.write(result.content)
                    f.write("\n\n")

if __name__ == '__main__':
    import asyncio
    from src.core.config import TEST_IMG_DIR, OUTPUT_TEX_PATH
    from src.llm.services.chapter_dispatcher import ChapterDispatcher
    from src.chapter.loader import load_chapters
    from src.llm.core.model.qwen import Qwen3P5PlusLLM

    chapters = load_chapters(TEST_IMG_DIR)
    llm = Qwen3P5PlusLLM()
    dispatcher = ChapterDispatcher(llm=llm, max_concurrency=10, max_retries=3)
    chapter_results = asyncio.run(dispatcher.run(chapters))

    writer = ChapterWriter(output_dir=OUTPUT_TEX_PATH)
    writer.write_tex(chapter_results, file_name="Sequence.tex")
