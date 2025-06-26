# cskel 项目开发计划

这是一个分阶段的计划，旨在帮助您构建 `cskel` 项目。我们将从核心功能开始，然后逐步添加命令行界面、配置和高级功能。

### 项目架构规划

我建议采用标准的 Python 项目结构，将核心逻辑与命令行界面分离。这将使代码更易于维护和测试。

```
cskel/
├── .git/
├── .gitignore
├── cskel/
│   ├── __init__.py
│   ├── cli.py          # 命令行界面 (使用 Typer 或 Click)
│   ├── constants.py    # 项目常量
│   ├── extractor.py    # 使用 LibCST 的核心代码转换逻辑
│   └── visitors.py     # 用于修改代码树的 LibCST 访问器/转换器
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_extractor.py
│   └── fixtures/         # 用于测试的示例 Python 文件
├── pyproject.toml      # 项目元数据和依赖项 (使用 Poetry 或 Hatch)
├── README.md
├── LICENSE
└── GEMINI.md
```

### 项目实施步骤

这是一个分阶段的实施计划，您可以一步步完成：

---

#### **阶段一：核心提取引擎**

*目标：创建一个能够将单个 Python 文件的函数体替换为 `pass` 的基本引擎。*

1.  **项目初始化**:
    *   创建上述目录结构。
    *   初始化 `pyproject.toml` 来管理项目依赖。主要依赖项将是 `libcst` 和 `typer`。
2.  **基础解析**:
    *   在 `extractor.py` 中，使用 `LibCST` 编写一个函数，该函数读取一个 Python 文件的内容，将其解析为具体语法树 (CST)，然后立即将其转换回代码。这可以验证“读取 -> 解析 -> 写回”的基本流程。
3.  **实现骨架化**:
    *   在 `visitors.py` 中，创建一个 `LibCST Transformer`。
    *   这个 Transformer 将访问函数定义 (`cst.FunctionDef`)，并将其主体替换为一个 `pass` 语句，同时保留函数签名、类型注解和文档字符串。
4.  **处理 `@code_level`**:
    *   修改 Transformer，使其能够识别并读取函数上的 `@code_level(N)` 装饰器。暂时只需读取级别，我们将在下一阶段根据它采取行动。

---

#### **阶段二：命令行界面与配置**

*目标：构建用户可用的 CLI，并使其能够响应配置文件。*

1.  **构建 CLI**:
    *   在 `cli.py` 中，使用 `typer` 实现 `cskel extract <源目录> --output <输出目录>` 命令。
    *   此命令将遍历源目录中的所有 `.py` 文件，应用第一阶段开发的 Transformer，并将转换后的代码写入输出目录，同时保持原始的目录结构。
2.  **加载配置**:
    *   在 `config.py` 中，编写逻辑来查找并解析项目根目录下的 `.skelignore` 和 `cskel.toml` 文件。
3.  **集成配置**:
    *   使用从 `.skelignore` 加载的模式来过滤要处理的文件。
    *   在 Transformer 中，使用从 `cskel.toml` 读取的 `min_level` 配置。如果一个函数的 `@code_level` 大于或等于 `min_level`，则保留其原始实现；否则，将其替换为 `pass`。

---

#### **阶段三：高级功能与测试**

*目标：实现智能调用分析和其余的 CLI 命令，并确保代码质量。*

1.  **实现“智能调用分析”**:
    *   增强 `LibCST Transformer`，使其在删除函数体之前，先访问其中的函数调用 (`cst.Call`)。
    *   收集这些调用的名称，将它们格式化为注释 (例如 `# → a.b.c()`)，然后将这些注释插入到被清空的函数体中。
2.  **实现 `preview` 和 `init` 命令**:
    *   `cskel preview`: 运行完整的提取逻辑，但将结果打印到控制台，而不是写入文件。
    *   `cskel init`: 在当前目录中创建模板 `.skelignore` 和 `cskel.toml` 文件。
3.  **编写测试**:
    *   在 `tests/` 目录中，为 `extractor` 和 `cli` 编写单元测试。
    *   在 `tests/fixtures/` 中放置一些示例 Python 文件，并断言生成的骨架代码与预期完全相符。

---

#### **阶段四：收尾与发布**

*目标：完成项目分析功能，完善文档，并准备发布。*

1.  **项目分析**:
    *   实现 `analyze_project` 功能，通过遍历项目的 CST 来统计函数、类和 `@code_level` 的覆盖率。
2.  **文档和打包**:
    *   更新 `README.md` 以反映所有已实现的功能。
    *   完善 `pyproject.toml`，为发布到 PyPI（Python 包索引）做准备。
    *   为代码库全面添加文档字符串和类型提示。

---