# Codex 指南
- 先运行 `pytest -q`，确保测试通过再进行修改。
- 新脚本必须写入 `.py` 文件，并在 `requirements.txt` 或 `setup.sh` 中声明依赖。
- 外部 API 调用要设置超时并重试 3 次，网络失败时应当读取本地回退数据。
- 不要删除 `sample_vix.csv`。
