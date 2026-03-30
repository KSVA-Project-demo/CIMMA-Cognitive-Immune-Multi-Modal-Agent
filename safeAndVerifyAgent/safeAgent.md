## safeAndVerifyAgent 说明（概要）

这是一个用于分析与生成对抗样本的智能体/工具集合（safeAndVerifyAgent），主要包含：

- 一个多模态对抗攻击框架：图像、文本、语音（路径：`multiModalAdversarialAttackFramework/src`）。
- 一个轻量级的机器人端调用/编排层（路径：`coreAgent-demo`），用于在机器人任务（识别分拣、路径规划/避障）中调度对抗攻击。

本文档简要说明模块划分、主要功能、如何使用智能体接口调度攻击，以及常用开发/测试步骤。

## 目录结构（关键文件）

- `multiModalAdversarialAttackFramework/src/`：对抗攻击实现代码（foolbox/ART 封装、TextFooler、音频攻击、目标检测、语义分割等）
	- `common.py`：统一的入口函数 `attacks(...)`，根据 task 参数分发到不同攻击流程。
	- `attack_init.py`：模型/数据/攻击器初始化工具（foolbox/ART 封装逻辑）。
	- `image_classification.py`, `object_detection.py`, `semantic_segmentation.py`, `audio_classification.py`, `attack_text.py`：各模态具体实现与脚本化入口。
	- `subprocess0319.py`：读取 `AE_thread_info.json` 并调用 `common.attacks(...)`（前端与脚本的桥梁）。

- `coreAgent-demo/`：机器人端轻量封装与演示代码
	- `adversarial_agent.py`：对框架的封装类 `AdversarialAgent`，负责写入 `AE_thread_info.json` 并启动 `subprocess0319.py`（可后台运行）。
	- `agentWorkflow.py`：机器人级对外智能体 `RobotAdversarialAgent`，封装多模态攻击的上层编排接口（`attack_image`、`attack_audio`、`attack_text`、`orchestrate_for_robot` 等）。
	- `agent_test.py`：轻量导入/构造测试脚本（不会触发实际攻击），用于验证模块可导入性。

## 设计与功能要点

- 多模态支持：图像（分类/检测/分割）、文本（自然语言攻击）、音频（语音分类攻击）。
- 最小侵入式集成：机器人端不直接依赖框架内部实现，而是通过写入 `AE_thread_info.json` 并调用 `subprocess0319.py` 来触发攻击，沿用框架现有 GUI/脚本流程。
- 后台/前台执行：agent 支持后台线程启动攻击进程（Daemon thread），方便机器人主循环不中断。
- 可扩展性：上层 `RobotAdversarialAgent.orchestrate_for_robot` 提供策略（policy）参数，可按任务（例如分拣/导航）选择要攻击的模态与攻击参数。

## 使用说明（快速开始）

下面示例在 Windows PowerShell 环境下，假设当前工作目录为仓库根目录 `D:\projectspycharm\CIMMA-demo`。

1) 基本导入并构造智能体（不启动实际攻击，仅构造）

```powershell
python .\safeAndVerifyAgent\coreAgent-demo\agent_test.py
```

你应看到类似输出：
- Framework src (test): <absolute path to multiModalAdversarialAttackFramework/src>
- RobotAdversarialAgent constructed successfully.

2) 从 Python 代码中以后台方式调度一次图像分类攻击（示例）

```powershell
python - <<"PY"
from agentWorkflow import RobotAdversarialAgent
import os

framework_src = r"d:\projectspycharm\CIMMA-demo\safeAndVerifyAgent\multiModalAdversarialAttackFramework\src"
agent = RobotAdversarialAgent(framework_src)
# 启动图像分类攻击（后台线程）
agent.attack_image(model_name='ResNet50', dataset_name='CIFAR10', method='L2ProjectedGradientDescentAttack', epsilons=[0.03], run_in_background=True)
print('attack scheduled')
PY
```

注意：真正执行攻击会消耗大量时间和计算资源，并且依赖模型权重与数据集路径（见 framework 内的 `model-weights/` 与 `data/` 目录）。

3) 从机器人编排（orchestrate_for_robot）示例

```python
from agentWorkflow import RobotAdversarialAgent
agent = RobotAdversarialAgent(r"d:\projectspycharm\CIMMA-demo\safeAndVerifyAgent\multiModalAdversarialAttackFramework\src")
perception = {'image': 'camera_frame.png', 'text': 'detected label'}
policy = {'image_model':'ResNet50', 'image_dataset':'CIFAR10', 'image_method':'L2ProjectedGradientDescentAttack', 'image_eps':[0.03], 'background':True}
agent.orchestrate_for_robot(perception, task='sorting', policy=policy)
```

## 输出与结果位置

- 对抗图像样本通常保存在 `multiModalAdversarialAttackFramework/adv-img/` 下，按 dataset/model/method/epsilon 分层。
- 目标检测的带框结果保存在 `multiModalAdversarialAttackFramework/results-img/object-detection/`。
- 语义分割的上色结果保存在 `multiModalAdversarialAttackFramework/results-img/semantic-segmentation/`。
- 音频对抗样本与波形图在 `multiModalAdversarialAttackFramework/results-audio/`。
- 框架还会在根目录写入 `AE_attackresult.json`、`record_content.txt`、`record_site.txt` 等用于前端显示与记录的临时文件。

## 开发者注意事项与调试建议

- 依赖：框架代码使用 PyTorch、foolbox、ART、TextFooler、yolov5 等第三方库。若要直接运行攻击，请确保环境已安装这些依赖（可参考 `multiModalAdversarialAttackFramework/environment.yml` 或 `setup.py`）。
- 路径：agent 写入的 `AE_thread_info.json` 必须放到 `.../multiModalAdversarialAttackFramework/src` 中（这是 `subprocess0319.py` 的读取位置）。`AdversarialAgent` 已处理此路径写入。
- 权重与数据：很多攻击需要预训练权重（位于 `model-weights/`）与测试数据（位于 `data/`）；如果缺少会报错或退出，请先准备好最小测试数据/权重或修改脚本以使用占位数据进行开发调试。
- 资源：部分攻击（特别是基于 BERT 或 AutoAttack）需要 GPU 才能在合理时间内完成；在资源不足时建议使用快速/基于噪声的攻击方法或将 `run_in_background=False` 以便查看即时错误。



