<div align="center">

  [![license](https://img.shields.io/github/license/new-soul-house/LLMPipeline.svg)](https://github.com/new-soul-house/LLMPipeline/tree/main/LICENSE)
  [![issue resolution](https://img.shields.io/github/issues-closed-raw/new-soul-house/LLMPipeline)](https://github.com/new-soul-house/LLMPipeline/issues)
  [![open issues](https://img.shields.io/github/issues-raw/new-soul-house/LLMPipeline)](https://github.com/new-soul-house/LLMPipeline/issues)

  <div>
    <a href="https://github.com/new-soul-house"><img src="https://img.shields.io/badge/NewSoul-新心靈舍-blue" /></a>&emsp;
    <a href="https://linluhe.github.io/qrcode.html"><img src="https://img.shields.io/badge/WeChat-微信-07c160" /></a>&emsp;
    <a href="https://linluhe.github.io/group_qrcode.html"><img src="https://img.shields.io/badge/WeChat-微信群-07c160" /></a>&emsp;
    <a href="https://space.bilibili.com/4557530/"><img src="https://img.shields.io/badge/Bilibili-B站-ff69b4" /></a>&emsp;
    <!-- visitor statistics logo 访问量统计徽标 -->
    <img src="https://komarev.com/ghpvc/?username=new-soul-house&label=Views&color=0e75b6&style=flat" alt="访问量统计" />
  </div>

  <p align="center">
    👋 join us on <a href="https://linluhe.github.io/group_qrcode.html" target="_blank">WeChat</a>
  </p>
</div>

# LLMPipeline

## Introduction
LLMPipeline is a Python package designed to optimize the performance of tasks related to Large Language Models (LLMs). It ensures efficient parallel execution of tasks while maintaining dependency constraints, significantly enhancing the overall performance.

LLMPipeline 是一个 Python 包，旨在优化与大语言模型 (LLM) 相关任务的性能。在满足依赖关系的前提下，确保任务的高效并行执行，从而显著提高整体性能。

## Features
- Dependency Management: Handles task dependencies efficiently, ensuring correct execution order.

  依赖管理：高效处理任务依赖关系，确保正确的执行顺序。
- Parallel Execution: Maximizes parallelism to improve performance.

  并行执行：最大化并行性以提高性能。
- Loop Handling: Supports tasks with loop structures.

  循环处理：支持带有循环结构的任务。
- Easy Integration: Simple and intuitive API for easy integration with existing projects.

  易于集成：简单直观的 API，便于与现有项目集成。

## Installation
You can install LLMPipeline via pip:

你可以通过 pip 安装 LLMPipeline：
```bash
pip install llmpipeline
```

## Usage
Here is a basic example to get you started:

下面是一个基本示例，帮助你快速入门：

```python
from llmpipeline import Pipeline

# Define your tasks
def task1():
    # Some processing
    return "output1"

def task2(input):
    # Some processing using input
    return "output2"

def task3():
    # Some processing
    return "output3"

# Initialize the pipeline
pipeline = Pipeline()

# Add tasks with dependencies
pipeline.add_task('task1', task1)
pipeline.add_task('task2', task2, dependencies=['task1'])
pipeline.add_task('task3', task3)

# Execute the pipeline
results = pipeline.run()

# Access the results
print(results)
```

## Documentation
For detailed documentation, please visit our official documentation page.

有关详细文档，请访问我们的官方文档页面。

## Contributing
We welcome contributions from the community. Please read our contributing guide to get started.

我们欢迎来自社区的贡献。请阅读我们的贡献指南开始。

## License
LLMPipeline is licensed under the Apache License Version 2.0. See the [LICENSE](./LICENSE) file for more details.

LLMPipeline 采用 Apache License Version 2.0 许可证。有关详细信息，请参阅[许可证](./LICENSE)文件。

## Acknowledgements
Special thanks to all contributors and the open-source community for their support.

特别感谢所有贡献者和开源社区的支持。

## Contact
For any questions or issues, please open an issue on our [GitHub repository](https://github.com/new-soul-house/LLMPipeline).

如有任何问题或意见，请在我们的[GitHub 仓库](https://github.com/new-soul-house/LLMPipeline)提交 issue。

<div align="center">
  
[![Star History Chart](https://api.star-history.com/svg?repos=new-soul-house/LLMPipeline&type=Date)](https://star-history.com/#new-soul-house/LLMPipeline&Date)

</div>
