# AI_Med_Assistant

AI_Med_Assistant 是一个基于知识图谱和大规模语言模型（LLM）的智能医疗常识问答系统。该系统结合了Neo4j知识图谱的强大检索能力和LLM的自然语言生成能力，为用户提供精准、个性化的医疗常识解答。

## 文件结构

```bash
AI_Med_Assistant
│  avatar_doctor.png         # 医生头像图片
│  avatar_user.png           # 用户头像图片
│  bubble_message.py         # 气泡式聊天窗口界面实现
│  build_medicalgraph.py     # 知识图谱构建脚本（首次运行时执行）
│  GPT.py                    # 大规模语言模型（LLM）的相关操作
│  KnowledgeRetriever.py     # 知识检索模块
│  main.py                   # 系统主程序入口
│  README.md                 # 项目说明文档
│  requirements.txt          # 项目所需依赖
│  wsPram.py                 # WebSocket 参数配置文件
│
├─config                     # 配置文件目录
├─data                       # 数据目录
├─dict                       # 自定义词典目录
```

## 运行环境

在运行此项目之前，请确保已安装以下环境：

- Python 3.8+
- Neo4j 4.0+ (请确保Neo4j数据库已经正确安装并启动)

## 安装依赖

```bash
pip install -r requirements.txt
```

## 系统运行步骤

### 1. 构建医疗知识图谱

首次运行时，需要先构建知识图谱。请确保Neo4j数据库已启动，并按照以下步骤执行：

```bash
python build_medicalgraph.py
```

此步骤将从项目提供的医疗数据文件中，构建Neo4j中的医疗知识图谱。**注意：**该过程可能较为耗时，请耐心等待。

图谱构建完成后，建议保存知识图谱数据，以便后续加载时无需重新构建。

### 2. 启动主程序

知识图谱构建完成后，可以直接运行系统主程序：

```bash
python main.py
```

该程序将启动基于LLM和知识图谱的医疗常识问答系统。用户可以通过图形界面与系统进行互动，输入医疗相关问题并获得智能解答。

## 注意事项

- **Neo4j 启动**：确保 Neo4j 在运行 `build_medicalgraph.py` 和 `main.py` 时始终处于启动状态。
- **数据保存**：知识图谱构建完成后，请及时保存数据，以便后续可以快速加载图谱。
- **依赖库**：根据 `requirements.txt` 安装所需的依赖库，确保程序运行环境正确配置。

