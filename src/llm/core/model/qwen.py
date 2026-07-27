import asyncio
from typing import List
from pathlib import Path
import dashscope
from dashscope import AioMultiModalConversation
from src.core.config import QWEN3P5_PLUS_MODEL, SYSTEM_PROMPT_PATH
from src.llm.core.model.interface import BaseLLM
from utils.system_prompt_parser import parse_system_prompt

class Qwen3P5PlusLLM(BaseLLM):
    def __init__(self):
        self.api_key=QWEN3P5_PLUS_MODEL["API_KEY"]
        dashscope.base_http_api_url=QWEN3P5_PLUS_MODEL["BASE_URL"]
        self.system_prompt = parse_system_prompt(SYSTEM_PROMPT_PATH)

    async def invoke(
            self,
            user_prompt: str,
            image_paths: List[Path] | None = None,
    ) -> str:
        conservation = AioMultiModalConversation()

        messages, content = [], []

        # 构造 messages 的系统提示词
        messages.append(
            {
                "role": "system",
                "content": [
                    {
                        "text": self.system_prompt
                    }
                ]
            }
        )

        # 构造 content(图片+标题)
        if image_paths:
            for image_path in image_paths:
                content.append(
                    {"image": f"file://{image_path.resolve()}"}
                )

        content.append(
            {"text": f"标题是{user_prompt}"}
        )

        # 构造 messages 的用户提示词
        messages.append(
            {
                "role": "user",
                "content": content
            }
        )

        response = await asyncio.wait_for(
            conservation.call(
                api_key=self.api_key,
                model=QWEN3P5_PLUS_MODEL['MODEL_NAME'],
                messages=messages
            ),
            timeout=900
        )

        return response.output.choices[0].message.content[0]["text"]


if __name__ == "__main__":
    from src.chapter.loader import load_chapters
    from src.core.config import TEST_IMG_DIR
    chapter = load_chapters(TEST_IMG_DIR)
    title, image_paths = chapter[0].title, chapter[0].images

    async def main():
        llm = Qwen3P5PlusLLM()
        response = await llm.invoke(user_prompt=title, image_paths=image_paths)
        print(response)

    asyncio.run(main())
