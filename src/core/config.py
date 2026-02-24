import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# 测试文件目录
TESTS_DIR = ROOT_DIR / "tests"
TEST_IMG_DIR = TESTS_DIR / "test_img"

# 用户图片的加载类型
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

# 模型配置
# qwen3-max
QWEN3_MAX_MODEL = {
    "MODEL_NAME": "qwen3-max",
    "API_KEY": os.getenv("QWEN3_MAX_API_KEY"),
    "BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1"
}