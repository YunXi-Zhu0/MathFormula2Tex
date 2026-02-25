from pathlib import Path
from typing import List
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    async def invoke(self, user_prompt: str, image_paths: List[Path]) -> str:
        """
        输入完整 prompt，返回模型原始字符串输出
        """
        pass
