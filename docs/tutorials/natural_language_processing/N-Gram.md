# N-Gram

## 介绍

N-Gram是一种基于统计语言模型的算法。它的基本思想是将文本里面的内容按照字节进行大小为N的滑动窗口操作，形成了长度是N的字节片段序列。每一个字节片段称为gram，对所有gram的出现频度进行统计，并且按照事先设定好的阈值进行过滤，形成关键gram列表，也就是这个文本的向量特征空间，列表中的每一种gram就是一个特征向量维度。

该模型基于这样一种假设，第N个词的出现只与前面N-1个词相关，而与其它任何词都不相关，整句的概率就是各个词出现概率的乘积。这些概率可以通过直接从语料中统计N个词同时出现的次数得到。常用的是二元的Bi-Gram和三元的Tri-Gram。

N-gram的用途很广，比如搜索引擎或者输入法提示，词性标注，垃圾短信分类，分词，机器翻译，语音识别能等等等。


## 概率计算

假设我们有一个由n nn个词组成的句子$S=(w_{1},w_{2},...,w_{n})$，如何衡量它的概率呢？让我们假设，每一个单词$w_{i}$都要依赖于从第一个单词$w_{1}$到到它之前一个单词$w_{i-1}$的影响：

$$p(S)=p(w_{1}w_{2}...w_{n})=p(w_{1})p(w_{2}|w_{1})...p(w_{n}|w_{n-1}...w_{2}w_{1})$$

这个衡量方法有两个缺陷:

1. 参数空间大： 概率$p(w_{n}|w_{n-1}...w_{2}w_{1})$的参数有O(n)个。
2. 数据稀疏，词同时出现的情况可能没有，组合阶数高时尤其明显。

为了解决第一个问题，引入马尔科夫假设（Markov Assumption）：一个词的出现仅与它之前的若干个词有关。

$$p(w_{1}...w_{n})=\prod{p(w_{i}|w_{i-1}...w_{1})} \approx \prod{p(w_{i}|w_{i-1}...w_{i-N+1})} $$

如果一个词的出现仅依赖于它前面出现的一个词，那么我们就称之为 Bi-gram：

$$p(S)=p(w_{1}w_{2}...w_{n})=p(w_{1})p(w_{2}|w_{1})...p(w_{n}|w_{n-1})$$

如果一个词的出现仅依赖于它前面出现的两个词，那么我们就称之为 Tri-gram：

$$p(S)=p(w_{1}w_{2}...w_{n})=p(w_{1})p(w_{2}|w_{1})...p(w_{n}|w_{n-1}w_{n-2})$$
N-gram的 N NN 可以取很高，然而现实中一般 bi-gram 和 tri-gram 就够用了.

用极大似然估计来计算每一项的条件概率，即频数：

$$p(w_{n}|w_{n-1})=\frac{C(w_{n-1}w_{n})}{C(w_{n-1})}$$

$$p(w_{n}|w_{n-1}w_{n-2})=\frac{C(w_{n-2}w_{n-1}w_{n})}{C(w_{n-2}w_{n-1})}$$

$$p(w_{n}|w_{n-1}...w_{2}w_{1})=\frac{C(w_{1}w_{2}...w_{n})}{C(w_{1}w_{2}...w_{n-1})}$$

具体地，以Bi-gram为例，我们有这样一个由三句话组成的语料库：

```
I am Sam
Sam I am
I do not like apple
```
容易统计，“I”出现了3次，“I am”出现了2次，因此能计算概率：

$$p(am|I)=\frac{2}{3}$$

同理，还能计算出如下概率：

$$p(Sam|am)=0.5$$

$$p(do|I)=0.33$$
等等



