import asyncio
from typing import List, Dict
from dataclasses import dataclass
from src.llm.core.model.interface import BaseLLM
from src.chapter.loader import Chapter

@dataclass
class ChapterResult:
    title: str
    success: bool
    content: str | None
    error: str | None

class ChapterDispatcher:
    def __init__(
        self,
        llm: BaseLLM,
        max_concurrency: int = 10,
        max_retries: int = 3
    ):
        self.llm = llm
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.max_retries = max_retries

    async def _process_one_chapter(self, chapter: Chapter) -> ChapterResult | None:
        async with self.semaphore:
            for attempt in range(self.max_retries):
                try:
                    print(f"[START] {chapter.title} (attempt {attempt + 1})")

                    result = await self.llm.invoke(
                        user_prompt=chapter.title,
                        image_paths=chapter.images
                    )

                    print(f"[Done] {chapter.title}")

                    return ChapterResult(
                        title=chapter.title,
                        success=True,
                        content=result,
                        error=None
                    )

                except Exception as e:
                    print(f"[ERROR] {chapter.title}: {e}")

                    if attempt == self.max_retries - 1:
                        return ChapterResult(
                            title=chapter.title,
                            success=False,
                            content=None,
                            error=str(e)
                        )

                    await asyncio.sleep(2 ** attempt)

    async def run(self, chapters: List) -> Dict[str, ChapterResult]:
        tasks = [
            self._process_one_chapter(chapter)
            for chapter in chapters
        ]

        results = await asyncio.gather(*tasks)

        return {r.title: r for r in results}

if __name__ == "__main__":
    from pprint import pprint
    from src.chapter.loader import load_chapters
    from src.core.config import TEST_IMG_DIR
    from src.llm.core.model.qwen import Qwen3P5PlusLLM

    chapters = load_chapters(TEST_IMG_DIR)
    llm = Qwen3P5PlusLLM()
    dispatcher = ChapterDispatcher(llm=llm, max_concurrency=10, max_retries=3)

    results = asyncio.run(dispatcher.run(chapters))

    pprint(results)
