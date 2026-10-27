# 看板离线翻译

GitHub Actions 每天北京时间 07:30 启动，抓取后在同一台 GitHub 标准 CPU 运行机上翻译新增论文标题和来源提供的完整摘要，再自动发布。定时任务可能延迟。电脑关机不影响。

## 正式配置

- `config/translation.json` 启用离线翻译。
- 模型：`Qwen3-4B-Instruct-2507`，Q4_K_M 权重（原始模型由 Qwen 发布，GGUF 量化由 bartowski 提供）；模型用于翻译，不调用 Qwen 在线 API。
- 推理引擎：`llama-cpp-python`，CPU；无翻译服务费用，不需要翻译 API Key。
- 公开权重首次下载约 2.50 GB，按作者发布的 SHA-256 校验，存于仓库目录之外并缓存。缓存被回收时会重新下载。
- 已有且来源未改变的 Qwen 译文保留。新译文存入 SQLite 的 `translations` 表，原有 `annotations` 和论文去重记录保留。
- 长摘要逐句翻译，长句再按词元数拆分，所有原文片段均送入模型。标题中的方法名保留；关键术语和百分比缺失时自动重试，必要时拆开原文复句重新翻译。碰到长度上限、异常思考内容或校验仍不通过时，不保存该条，后续重试。机译仍可能存在语义或术语误差；页面保留英文原文供核对。
- 默认每次最多处理 200 篇、翻译预算 60 分钟，GitHub 单轮上限 90 分钟。先保存并发布已完成的部分，再执行覆盖检查；缺译时 Actions 报错、页面标明待补齐，次日从已保存的进度继续。
- 不生成或伪造科研短评。既有短评保留，每日总览与一句点评仍由独立的原有 agent 流程负责。
- 日常翻译不读取 `USTC_LLM_KEY`，也不读取任何聊天记录。该 Secret 留在原处，手动连通检查仍可使用。

## 运行

需要 Python 3.12。在独立环境中安装 `requirements-translation.txt`，然后：

```sh
python -B -m radar.offline_translate prepare
python -B -m radar run
python -B -m radar.offline_translate verify
```

GitHub 工作流已包含安装、模型缓存、准备、回归检查、抓取与翻译、覆盖检查、提交和发布。模型不会写入公开仓库或浏览器页面。

## 模型与软件来源

- [Qwen3-1.7B 官方模型说明与 Apache 2.0 许可](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
- [GGUF 量化权重与来源说明](https://huggingface.co/bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF)
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- [GitHub 标准运行机计费说明](https://docs.github.com/en/billing/concepts/product-billing/github-actions)

`offline-translation-check` 和已停用的 `hymt-translation-check` 是选型时的只读试验，均不写论文数据库，也不参与日常发布。正式模型使用 `qwen-offline-check` 试译验证；不会把试验模型的结果混入已有译文。
