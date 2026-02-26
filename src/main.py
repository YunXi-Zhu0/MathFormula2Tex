import asyncio
from pathlib import Path
from src.chapter.loader import load_chapters
from src.llm.core.model.qwen import Qwen3P5PlusLLM
from src.llm.services.chapter_dispatcher import ChapterDispatcher
from src.tex.chapter_writer import ChapterWriter


async def run_workflow(
    input_dir: Path,
    output_dir: Path,
):
    # 1️⃣ 加载章节
    print("[INFO] 正在加载章节...")
    chapters = load_chapters(input_dir)
    print(f"[INFO] 共找到 {len(chapters)} 个章节")

    # 2️⃣ 初始化 LLM
    llm = Qwen3P5PlusLLM()

    # 3️⃣ 初始化调度器
    dispatcher = ChapterDispatcher(
        llm=llm,
        max_concurrency=10,
        max_retries=3
    )

    # 4️⃣ 异步处理
    print("[INFO] 开始处理章节...")
    chapter_results = await dispatcher.run(chapters)
    print("[INFO] 所有章节处理完成")

    # 5️⃣ 打印结果
    for title, result in chapter_results.items():
        if result.success:
            print(f"✅ {title} LLM分析成功")
        else:
            print(f"❌ {title} LLM分析失败: {result.error}")

    # 6️⃣ 写入 tex
    writer = ChapterWriter(output_dir=output_dir)
    writer.write_tex(chapter_results, file_name="AllChapters.tex")

    print(f"[INFO] 已写入文件: {output_dir / 'AllChapters.tex'}")


if __name__ == "__main__":
    from src.core.config import INPUT_IMG_DIR, OUTPUT_TEX_PATH

    asyncio.run(
        run_workflow(
            input_dir=INPUT_IMG_DIR,
            output_dir=OUTPUT_TEX_PATH,
        )
    )
