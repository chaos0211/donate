

# hive_app — Predict 模块说明（后端）

本文档说明 `backend/app/predict/` 下各目录与文件的作用，方便快速理解与二次开发。该模块采用“可插拔算法 + 分层职责”的结构，当前默认算法为 **LSTM**，后续可扩展 GRU/Transformer 等。

---

## 目录总览

```
backend/app/predict/
  core/                         # 通用协议与注册表
    types.py                    # 数据构建输出的类型描述（TypedDict）
    registry.py                 # 算法注册表（供前端“算法选择”）

  data/                         # 数据集与特征工程
    builders.py                 # 全局分区样本构建器（按 country/device/brand 聚合所有 app）
    features.py                 # 特征工程工具与配置（时序/静态/关键词哈希）

  models/                       # 模型定义（统一基类，可插拔）
    base.py                     # BaseModelWrapper 抽象基类（规定 forward(x_seq, x_static) 接口）
    lstm.py                     # GlobalLSTM：LSTM + 可选注意力 + 静态分支 MLP，多步输出

  train/                        # 训练流程
    callbacks.py                # EarlyStopping 等回调
    metrics.py                  # MAE 等指标（可拓展）
    trainer.py                  # Trainer：训练/验证/早停/学习率调度/梯度裁剪
    cli.py                      # 训练 CLI：从 DB 构建数据 → 训练 → 保存 pt

  infer/                        # 推理封装
    predictor.py                # Predictor：加载 pt → 单样本预测（未来 horizon 天）

  io/                           # 模型文件路径与保存/加载
    paths.py                    # 路径管理：global_{country}_{device}_{brand}_{algo}.pt
    save_load.py                # 保存/加载 bundle（state_dict + meta）与模型重建

  api/                          # 面向 FastAPI 的服务封装（被 api/v1 调用）
    service.py                  # forecast_global：加载全局模型 → 针对某 app 预测
```

> 说明：**全局模型**指按 `(country, device, brand)` 聚合过去一年+所有 app 的历史训练一个 pt 文件；在线预测对任意 app 复用该 pt。

---

## 各文件职责详解

### core/
- **`types.py`**  
  定义构建数据集的标准返回结构（`BuildOutput`），便于在模块间传递 `X_seq / X_static / y / ids / dates`。

- **`registry.py`**  
  维护算法注册表，前端“算法选择”按钮可对应到注册名（如 `lstm`）。新增算法时在此 `@register("algo_name")` 即可。

### data/
- **`features.py`**  
  - 时间相关工具：`to_date`、`dow_feats`；
  - 关键词哈希：`hash_bow`（将关键字 Bag-of-Words 映射为固定维度稠密向量）；
  - 特征配置：`SeqFeatureConfig`（时序侧）、`StaticFeatureConfig`（静态侧，可开关 price/rating/age/keyword_hash 等）。

- **`builders.py`**  
  - 从 `app_ratings` 读取 `(country, device, brand)` 分区的**所有 app**；
  - 保证**按日连续**（缺失天前向填补）；
  - 构造**时序特征**（如 `rank_norm`、`diff`、`MA7`、`dow_sin/cos`）与**静态特征**（`price/is_ad/rating/log1p(rating_num)/age/keywords-hash`）；
  - 以滑动窗口切成样本：`X_seq [N, lookback, F_seq]`、`X_static [N, F_static]`、`y [N, horizon]`；
  - 返回包含 `ids`（app_id）与 `dates`（窗口末日）便于时间切分与回测。

### models/
- **`base.py`**  
  - 定义抽象基类 `BaseModelWrapper`，强制所有模型实现 `forward(x_seq, x_static)`，实现统一接口。

- **`lstm.py`**  
  - `GlobalLSTM`：序列侧 LSTM（可选 Multihead Attention），静态侧 MLP；
  - 融合后经 MLP 输出 `horizon` 维（一次性多步预测）。

### train/
- **`metrics.py`**  
  - 目前提供 `mae`（均值绝对误差），后续可扩展 RMSE/MAPE/R2 等。

- **`callbacks.py`**  
  - `EarlyStopping`：验证集指标长时间不提升则提前停止。

- **`trainer.py`**  
  - 训练主循环：训练/验证、`ReduceLROnPlateau` 调度、梯度裁剪、记录最优权重。

- **`cli.py`**  
  - 训练入口：
    1. 通过 `build_global_samples` 构建一年期全局样本；
    2. **按时间排序**做 80/20 训练/验证切分（避免时间泄漏）；
    3. 用 `GlobalLSTM` 训练并早停；
    4. 保存 `pt` 为 `backend/models/lstm/global_{country}_{device}_{brand}_lstm.pt`（包含 `state_dict + meta`）。

### infer/
- **`predictor.py`**  
  - 从磁盘加载 `pt`，根据 `meta` 重建模型；
  - `forecast(x_seq, x_static)`：返回未来 `horizon` 天的标准化排名预测（外层可反归一化为名次）。

### io/
- **`paths.py`**  
  - 统一管理模型文件路径，默认目录可通过 `PREDICT_MODEL_DIR` 覆盖。

- **`save_load.py`**  
  - 保存/加载 `bundle`（`state_dict + meta`）并据 `meta` 还原模型实例。

### api/
- **`service.py`**  
  - `forecast_global(...)`：面向 FastAPI 使用的服务函数：加载全局模型 → 构造该 app 的单样本 → 推理 → 返回未来 N 天名次（已反归一化）。

---

## 训练与推理快速上手

### 训练（以 us / iphone / free 分区为例）
```bash
python -m app.predict.train.cli \
  --country us --device iphone --brand free \
  --days 420 --lookback 30 --horizon 7 \
  --epochs 40 --batch 256
```
### 参数说明
- `--country`：国家代码，例如 us、cn。
- `--device`：设备类型，例如 iphone、ipad。
- `--brand`：榜单类型，例如 free（免费）、paid（付费）、grossing（畅销）。
- `--days`：历史数据天数，例如 420 表示用最近约 14 个月数据。
- `--lookback`：输入序列长度（天），模型每次看到的历史窗口大小。
- `--horizon`：预测的未来天数。
- `--epochs`：最大训练轮数。
- `--batch`：训练批次大小（每次迭代使用的样本数）。
- 
产物：`backend/predict/models/lstm/global_us_iphone_free_lstm.pt`

### 在线推理（在 FastAPI 路由中调用）
- 通过 `app.predict.api.service.forecast_global` 进行预测；
- 或使用 `infer.Predictor` 手动加载并调用 `forecast`；
- 输出为未来 `horizon` 天的预测名次（已做简单反归一化，默认 `MAX_RANK=200`）。

---

## 设计要点与扩展建议
- **可插拔算法**：在 `core/registry.py` 注册新算法（如 `gru`、`transformer`），前端下拉即可切换；
- **时间切分**：严格按时间做 train/val，避免未来信息泄漏；
- **特征扩展**：可按需在 `features.py`/`builders.py` 添加更多滚动统计/趋势/波动/类别 embedding；
- **关键词**：采用 Hash Trick 降维（固定维度、无需词典），也可替换为 TF-IDF/自训练 embedding；
- **线上稳定性**：训练脚本与服务使用同一套特征管线，推理不依赖即刻重算滚动（模型为“一次性多步输出”）。

---

如需把更多算法接入（GRU/Transformer）或将该模块接到前端（算法选择、曲线可视化、回测评估），可在此文档继续追加对应小节。

# us / iphone / free
python -m app.predict.train.cli \
  --country us --device iphone --brand free \
  --days 420 --lookback 30 --horizon 7 \
  --epochs 40 --batch 256

# us / iphone / paid
python -m app.predict.train.cli \
  --country us --device iphone --brand paid \
  --days 420 --lookback 30 --horizon 7 \
  --epochs 40 --batch 256

# us / iphone / grossing
python -m app.predict.train.cli \
  --country us --device iphone --brand grossing \
  --days 420 --lookback 30 --horizon 7 \
  --epochs 40 --batch 256

# cn / iphone / free
python -m app.predict.train.cli \
  --country cn --device iphone --brand free \
  --days 420 --lookback 30 --horizon 7 \
  --epochs 40 --batch 256

# cn / iphone / paid
python -m app.predict.train.cli \
  --country cn --device iphone --brand paid \
  --days 420 --lookback 30 --horizon 7 \
  --epochs 40 --batch 256

# cn / iphone / grossing
python -m app.predict.train.cli \
  --country cn --device iphone --brand grossing \
  --days 420 --lookback 30 --horizon 7 \
  --epochs 40 --batch 256