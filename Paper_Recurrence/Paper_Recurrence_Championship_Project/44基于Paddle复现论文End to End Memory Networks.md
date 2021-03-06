# End-To-End-Memory-Networks-in-Paddle
## 一、模型介绍
原论文地址：[Sainbayar Sukhbaatar, Arthur Szlam, Jason Weston, Rob Fergus: “End-To-End Memory Networks”, 2015.](https://arxiv.org/pdf/1503.08895v5.pdf)

参考repo：[https://github.com/facebookarchive/MemNN](https://github.com/facebookarchive/MemNN)

项目AiStudio地址：[https://aistudio.baidu.com/aistudio/projectdetail/2381004](https://aistudio.baidu.com/aistudio/projectdetail/2381004)

![模型简介](https://ai-studio-static-online.cdn.bcebos.com/25aecee52aac46b98e67c04d903f81dd6a65f7661ed44a8c9ab2ae419cd87068)

本模型是Facebook AI在Memory networks之后提出的一个更加完善的记忆网络模型，在问答系统以及语言模型中均有良好的应用。论文中使用了多个单层单元堆叠而成的多层架构。

单层架构如上图a所示，主要的参数包括A,B,C,W四个矩阵，其中A,B,C三个矩阵就是embedding矩阵，主要是将输入文本和Question编码成词向量，W是最终的输出矩阵。从上图可以看出，对于输入的句子s分别会使用A和C进行编码得到Input和Output的记忆模块，Input用来跟Question编码得到的向量相乘得到每句话跟q的相关性，Output则与该相关性进行加权求和得到输出向量。然后再加上q并传入最终的输出层。

多层网络如上图b所示，实际上是将多个单层堆叠到一起形成的网络，这里将每一层称为一个hop。
为了减少参数，模型提出了两种让各个hop之间共享Embedding参数（A与C）的方法：
* Adjacent：这种方法让相邻层之间的$A=C$。也就是说$A_{k+1}=C_{k}$，此外W等于顶层的C，B等于底层的A，这样就减少了一半的参数量。
* Layer-wise（RNN-like)：与RNN相似，采用完全共享参数的方法，即各层之间参数均相等。$A_{1}=A_{2}=...=A_{k}$,$C_{1}=C_{2}=...=C_{k}$。但这样模型的参数太少，性能会受到影响，故提出一种改进方法，在每一层之间加一个线性映射矩阵H，即令$u^{k+1}=H u^{k}+o^{k}$。

具体到语言模型，模型做出了一下调整：
1. 由于输入是单个句子，编码级别是单词级的，所以可以直接将每个单词的词向量存入memory即可，也就是说A与C现在都是单词的Embedding矩阵，mi与ci中都是单个单词的词向量。
2. 输出W矩阵的output为下一个单词的概率，即输出维度为vocab size。
3. 不同于QA任务，这里不存在Question，所以直接将q向量设置为全0.1的常量，也不需要再进行Embedding操作。
4. 采用Layer-wise的参数缩减策略。
5. 文中提出，对于每一层的u向量中一半的神经元进行ReLU操作，以帮助模型训练。

## 二、复现精度

相应模型已包含在本repo中，分别位于目录`models_ptb`与`models_text8`下

| Dataset | Paper Perplexity | Our Perplexity |
| :-----: | :--------------: | :------------: |
|   ptb   |       111        |     110.75     |
|  text8  |       147        |     145.62     |

## 三、数据集

* Penn Treetank:

    * [Penn Treebank](https://aistudio.baidu.com/aistudio/datasetdetail/108805)

        train：887k words

        valid：70k words

        test：78k words

        vocabulary  size：10k

    * [text8](https://aistudio.baidu.com/aistudio/datasetdetail/108807)

        train：总共100M个字符，划分为93.3M/5.7M/1M字符(train/valid/test)，将出现次数少于10次的单词替换为<UNK>

## 四、环境依赖

* 硬件：GPU
* 框架：Paddle >= 2.0.0，progress库

## 五、快速开始


```python
# 取出数据集
!mv data/*/* data/
# 安装依赖
!pip install -r requirements.txt
```

### 训练
训练参数可在`config.py`文件中调整。

Note: 由于本模型受随机因素影响较大，故每次训练的结果差异较大，即使固定随机种子，由于GPU的原因训练结果仍然无法完全一致。

#### 在ptb数据集上训练


```python
!cp config/config_ptb config.py
!python train.py
```

#### 寻找最佳模型

由于模型受随机因素影响较大，故要进行多次训练来找到最优模型，原论文中在ptb数据集上进行了10次训练，并保留了在test集上表现最好的模型。本复现提供了一个脚本，来进行多次训练以获得能达到足够精度的模型。


```python
!cp config/config_ptb config.py
!python train_until.py --target 111.0
```

以下是在ptb数据集上进行多次训练以达到目标精度的[log](./log/ptb_train_until.log)

#### 在text8数据集上训练


```python
!cp config/config_text8 config.py
!python train.py
```

### 测试

保持`config.py`文件与训练时相同


```python
!python eval.py
```


### 使用预训练模型

#### ptb数据集上



```python
!cp config/config_ptb_test config.py
!python eval.py
```

    Read 887521 words from data/ptb.train.txt
    Read 70390 words from data/ptb.valid.txt
    Read 78669 words from data/ptb.test.txt
    vacab size is 10000
    W0917 14:53:32.570137   801 device_context.cc:404] Please NOTE: device: 0, GPU Compute Capability: 7.0, Driver API Version: 10.1, Runtime API Version: 10.1
    W0917 14:53:32.573897   801 device_context.cc:422] device: 0, cuDNN Version: 7.6.
    Test |#####################           | 67.7% | ETA: 4s

将得到以下结果

![](https://ai-studio-static-online.cdn.bcebos.com/be02b7e3bb3b4c2093256671295da87ea553af750f7641d8a55278f201f6b4ee)


#### text8数据集上


```python
!cp config/config_text8_test config.py
!python eval.py
```

结果如下

![](https://ai-studio-static-online.cdn.bcebos.com/12461a33b1e14d228811a74fcb92cff38198fd0962b2496e989d2d32af360ea5)


## 六、代码结构详细说明

### 6.1 代码结构

```
├── checkpoints
├── config                                        # 配置文件模板
│   ├── config_ptb
│   ├── config_ptb_test
│   ├── config_text8
│   └── config_text8_test
├── data                                        # 数据集
│   ├── ptb.test.txt
│   ├── ptb.train.txt
│   ├── ptb.valid.txt
│   ├── ptb.vocab.txt
│   ├── text8.test.txt
│   ├── text8.train.txt
│   ├── text8.valid.txt
│   └── text8.vocab.txt
├── models_ptb                                    # ptb数据集上的预训练模型
│   └── model_17814_110.75
├── models_text8                                # text8数据集上的预训练模型
│   └── model_500_7_100_145.62
├── images                                        # 图片目录
│   ├── ptb.png
│   └── text8.png
├── config.py
├── data.py
├── eval.py                                        # 测试脚本
├── train.py                                    # 训练脚本
├── model.py
├── README_cn.md
├── README.md
├── requirements.txt
├── train_until.py
└── utils.py
```

### 6.2 参数说明

可以在`config.py`中设置以下参数

```
config.edim = 150                       # internal state dimension
config.lindim = 75                      # linear part of the state
config.nhop = 7                         # number of hops
config.mem_size = 200                   # memory size
config.batch_size = 128                 # batch size to use during training
config.nepoch = 100                     # number of epoch to use during training
config.init_lr = 0.01                   # initial learning rate
config.init_hid = 0.1                   # initial internal state value
config.init_std = 0.05                  # weight initialization std
config.max_grad_norm = 50               # clip gradients to this norm
config.data_dir = "data"                # data directory
config.checkpoint_dir = "checkpoints"   # checkpoint directory
config.model_name = "model"             # model name for test and recover train
config.recover_train = False            # if True, load model [model_name] before train
config.data_name = "ptb"                # data set name
config.show = True                      # print progress, need progress module
config.srand = 17814                    # initial random seed
```
