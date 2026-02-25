# 🧮 MathFormula2Tex

基于多模态大语言模型（LLM）的**数学公式图片转 LaTeX** 工具。将按章节组织的题目/公式图片批量识别并转换为符合规范的 LaTeX 代码，输出为可编译的 `.tex` 文件。

---

## 📚 目录

- [项目简介](#项目简介)
- [项目架构](#项目架构)
- [工作流程](#工作流程)
- [用户使用说明](#用户使用说明)
- [用户自定义模型](#用户自定义模型)
- [开发与测试](#开发与测试)

---

## ✨ 项目简介

- **功能**：从 `input/` 下按「一章一文件夹」组织的图片（如数学题、公式截图）出发，调用视觉 LLM 识别内容，按既定排版规范生成 LaTeX，并合并写入 `output/` 下的单个 `.tex` 文件。
- **默认模型**：通义千问 **qwen3.5-plus**（阿里云 DashScope API），支持多图 + 文本的多模态输入。
- **技术栈**：Python 3.14+、异步并发、DashScope SDK、python-dotenv。

---

## 🧱 项目架构

```
MathFormula2Tex/
├── src/
│   ├── main.py                 # 程序入口，串联加载→调度→写入
│   ├── core/
│   │   └── config.py           # 路径、模型、提示词等配置
│   ├── chapter/
│   │   └── loader.py           # 章节扫描与 Chapter 数据结构
│   ├── llm/
│   │   ├── core/
│   │   │   ├── model/
│   │   │   │   ├── interface.py   # BaseLLM 抽象接口
│   │   │   │   └── qwen.py        # 通义千问多模态实现
│   │   │   └── prompt/
│   │   │       └── system_prompt.md  # 系统提示词（LaTeX 规范）
│   │   └── services/
│   │       └── chapter_dispatcher.py  # 章节异步调度与重试
│   └── tex/
│       └── chapter_writer.py    # 将章节结果写入 .tex 文件
├── utils/
│   └── system_prompt_parser.py  # 系统提示词解析（读入 .md）
├── input/                      # 用户图片输入（按章节分子目录）
├── output/                     # 生成的 .tex 输出
├── tests/
│   └── test_img/               # 测试用图片（可选）
├── .env                        # 环境变量（API Key 等，不提交）
├── pyproject.toml              # 项目与依赖
└── README.md
```

### 模块职责

| 模块 | 职责 |
|------|------|
| `config` | 根目录、输入/输出路径、支持的图片后缀、模型配置（名称/API Key/Base URL）、系统提示词路径 |
| `chapter.loader` | 扫描 `input` 下子目录，每个子目录视为一章，收集其中的 `.jpg/.jpeg/.png`，构造 `Chapter(title, images)` 列表 |
| `llm.core.model.interface` | 定义 `BaseLLM.invoke(user_prompt, image_paths) -> str`，统一多模态调用契约 |
| `llm.core.model.qwen` | 使用 DashScope `AioMultiModalConversation` 调用 qwen3.5-plus，拼接系统提示词 + 图片 + 章节标题 |
| `llm.services.chapter_dispatcher` | 异步并发调度各章节，信号量限流、失败重试，汇总为 `Dict[title, ChapterResult]` |
| `tex.chapter_writer` | 按章节顺序将成功的 `ChapterResult.content` 写入单个 `.tex` 文件 |

---

## 🔄 工作流程

1. **加载章节**  
   从 `INPUT_IMG_DIR`（默认 `input/`）扫描子目录，每个子目录名作为章节标题，其下图片列表作为该章的 `images`，得到 `List[Chapter]`。

2. **初始化 LLM 与调度器**  
   实例化 `Qwen3P5PlusLLM()`（或自定义的 `BaseLLM` 实现），再创建 `ChapterDispatcher(llm, max_concurrency=10, max_retries=3)`。

3. **异步处理章节**  
   对每个 `Chapter` 调用 `llm.invoke(user_prompt=chapter.title, image_paths=chapter.images)`，调度器负责并发与重试，得到 `chapter_results: Dict[str, ChapterResult]`。

4. **写入 TeX**  
   `ChapterWriter` 按章节顺序遍历 `chapter_results`，将 `result.content` 依次写入 `output/AllChapters.tex`（失败章节会打印错误并跳过写入）。

5. **结果**  
   控制台输出每章成功/失败状态；`output/AllChapters.tex` 可直接用于 LaTeX 编译（需自行保证导言区与宏如 `\lfive`、`\ltwo` 等已定义）。

---

## 🚀 用户使用说明

### 环境要求

- **Python**：>= 3.14（见 `pyproject.toml`）
- **网络**：可访问阿里云 DashScope API（默认 `https://dashscope.aliyuncs.com/api/v1`）

### 安装

```bash
# 克隆或进入项目目录
cd MathFormula2Tex

# 使用uv管理器同步依赖（推荐）
uv sync
```

### 配置

1. **API Key**  
   在项目根目录创建 `.env`，配置通义千问 API Key：

   ```env
   QWEN3P5_PLUS_API_KEY=sk-xxxxxxxx
   ```

   `config.py` 通过 `os.getenv("QWEN3P5_PLUS_API_KEY")` 读取；若使用其它变量名，需同步修改 `config.py` 中的 `QWEN3P5_PLUS_MODEL["API_KEY"]`。

2. **输入目录结构**  
   在 `input/` 下按「一章一个子目录」放置图片，子目录名会作为该章标题传给 LLM 并用于生成 `\section*{...}`：

   ```
   input/
   ├── 一、等差数列的基本公式/
   │   ├── 1.jpg
   │   ├── 2.png
   │   └── ...
   ├── 二、等比数列/
   │   └── ...
   └── 三、待定系数法/
       └── ...
   ```

   支持的图片格式：`.jpg`、`.jpeg`、`.png`（由 `config.IMAGE_EXTENSIONS` 控制）。

3. **输出目录**  
   默认输出目录为 `output/`，可在 `main.py` 中通过 `OUTPUT_TEX_PATH` 修改；`ChapterWriter` 会自动创建目录。

### 运行

在项目根目录执行：

```bash
python -m src.main
```

或：

```bash
python src/main.py
```

运行后将在控制台看到各章节处理进度与成败，生成的 LaTeX 文件路径为：`output/AllChapters.tex`。

### 修改输出文件名

在 `src/main.py` 中调整 `ChapterWriter.write_tex(..., file_name="AllChapters.tex")` 的 `file_name` 参数即可。

---

## 🧩 用户自定义模型

### 1. 实现 BaseLLM 接口

所有模型需实现 `src/llm/core/model/interface.py` 中的抽象接口：

```python
from pathlib import Path
from typing import List
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    async def invoke(self, user_prompt: str, image_paths: List[Path]) -> str:
        """输入章节标题与图片路径列表，返回模型原始字符串（即本节 LaTeX 片段）。"""
        pass
```

- `user_prompt`：当前章节标题（如 `"一、等差数列的基本公式"`）。
- `image_paths`：该章下图片的本地路径列表，顺序与目录扫描顺序一致。
- 返回值：纯 LaTeX 文本（不要包含 Markdown 代码块包裹），系统提示词中已要求模型只输出 LaTeX。

### 2. 添加新模型步骤

1. 在 `src/llm/core/model/` 下新建模块（如 `my_model.py`），实现一个类继承 `BaseLLM`，在 `invoke` 中完成：
   - 读取/拼接系统提示词（可复用 `utils.system_prompt_parser.parse_system_prompt(SYSTEM_PROMPT_PATH)` 或自定义路径）；
   - 将 `image_paths` 转为当前 API 所需格式（如 file URL、base64 等）；
   - 调用对应 API（同步接口可用 `asyncio.to_thread` 或等效方式封装为 async）；
   - 从响应中提取纯文本并 return。
2. 在 `src/core/config.py` 中为该模型增加配置（如 `MY_MODEL_API_KEY`、`MY_MODEL_BASE_URL`、模型名等），并从 `.env` 读取敏感信息。
3. 在 `src/main.py` 中将对 `Qwen3P5PlusLLM()` 的实例化改为您的模型类，例如：

   ```python
   from src.llm.core.model.my_model import MyCustomLLM
   llm = MyCustomLLM()
   ```

调度器 `ChapterDispatcher` 与章节加载、写入逻辑无需修改，只要 LLM 实现符合 `BaseLLM` 即可。

### 3. 自定义系统提示词

- **路径**：默认在 `src/llm/core/prompt/system_prompt.md`，由 `config.SYSTEM_PROMPT_PATH` 指定。
- **内容**：定义「角色 + 任务 + 输出格式 + 题型规范 + 禁止事项」等，当前包括：
  - 标题生成规则（`\section*{title}` + `enumerate`）；
  - 单选题、多选题、填空题、解答题/小问的 LaTeX 模板；
  - 视觉模型转写错误防控（符号易混清单）；
  - 严格禁止解题、写答案、加解析等；
  - 行内公式用 `\( ... \)`、题号由 LaTeX 自动生成等。

修改 `system_prompt.md` 后无需改代码，下次运行会自动加载；若更换路径，需在 `config.py` 中修改 `SYSTEM_PROMPT_PATH`，并在新模型实现中读取该路径（或继续使用 `parse_system_prompt`）。

### 4. 配置项汇总（config.py）

| 配置项 | 说明 | 自定义方式 |
|------|------|------------|
| `INPUT_IMG_DIR` | 图片根目录 | 修改 `config.py` 或通过环境变量+代码扩展 |
| `OUTPUT_TEX_PATH` | .tex 输出目录 | 同上 |
| `IMAGE_EXTENSIONS` | 支持的图片后缀 | 修改 `config.py` 中集合 |
| `QWEN3P5_PLUS_MODEL` | 模型名、API Key、Base URL | 修改 `config.py`，API Key 建议放 `.env` |
| `SYSTEM_PROMPT_PATH` | 系统提示词 .md 路径 | 修改 `config.py` |

---

## 🧪 开发与测试

- **依赖管理**：`pyproject.toml`（`requires-python = ">=3.14"`，依赖 `dashscope`、`python-dotenv`、`pytest`）。注意：代码中通过 `dotenv` 加载 `.env`，包名一般为 `python-dotenv`，若安装失败请用 `pip install python-dotenv`。
- **测试**：`tests/test_img` 可作为测试图片目录（见 `chapter/loader.py` 与 `chapter_dispatcher.py` 的 `if __name__ == "__main__"`）；可配置 `TEST_IMG_DIR` 指向 `tests/test_img`，单独运行各模块进行调试。
- **忽略**：`.gitignore` 已忽略 `input/`、`output/`、`.env`、`.venv`、`tests/test_img` 等，避免将本地数据与密钥提交。

---

## ⚖️ 许可证与免责声明

(1) 本项目仅供学习与内部使用\
(2) 使用通义千问等第三方 API 时请遵守对应服务条款与计费规则\
(3) 生成的 LaTeX 请自行校对后再用于正式排版
