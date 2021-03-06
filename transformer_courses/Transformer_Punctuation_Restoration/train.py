
# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time

import yaml 
import argparse 
from pprint import pprint
from attrdict import AttrDict

import paddle
from paddlenlp.transformers import LinearDecayWithWarmup
from paddlenlp.transformers import TransformerModel, InferTransformerModel, CrossEntropyCriterion, position_encoding_init
from paddlenlp.utils.log import logger
from paddlenlp.datasets import DatasetBuilder
from paddlenlp.transformers import ElectraForTokenClassification, ElectraTokenizer
from paddlenlp.data import Stack, Tuple, Pad, Dict

from dataloader import create_train_dataloader, load_dataset
from utils import compute_metrics, evaluate

import paddle.distributed as dist
 
import yaml 
import argparse 
from pprint import pprint
from attrdict import AttrDict

import paddle
from paddle.io import DataLoader  

import os
import pandas as pd
from sklearn.metrics import classification_report
from functools import partial
 
def do_train(args):
    last_step =  args.num_train_epochs * len(train_data_loader)
    tic_train = time.time()

    for epoch in range(args.num_train_epochs):
        for step, batch in enumerate(train_data_loader):
            args.global_step += 1
            # print('~~~~~~~~~~~~~~~~~~~~~args.global_step',args.global_step)
            input_ids, token_type_ids, _, labels = batch
            logits = model(input_ids, token_type_ids)
            loss = loss_fct(logits, labels)
            avg_loss = paddle.mean(loss) 

            if args.global_step % args.logging_steps == 0:
                print("global step %d, epoch: %d, batch: %d, loss: %f, speed: %.2f step/s"
                        % (args.global_step, epoch, step, avg_loss,
                        args.logging_steps / (time.time() - tic_train)))
                tic_train = time.time()

            avg_loss.backward()
            optimizer.step()
            lr_scheduler.step()
            optimizer.clear_grad()

            if args.global_step % args.save_steps == 0 or args.global_step == last_step:
                if paddle.distributed.get_rank() == 0:
                        evaluate(model, loss_fct, valid_data_loader, label_num)
                        paddle.save(model.state_dict(),os.path.join(args.output_dir, "model_%d.pdparams" % args.global_step))

# ????????????
if __name__ == '__main__':
    # ????????????
    yaml_file = './electra.base.yaml'
    with open(yaml_file, 'rt') as f:
        args = AttrDict(yaml.safe_load(f))
    
    paddle.set_device(args.device) # ??????gpu?????????????????????paddlepaddle-gpu
    
    train_data_loader, valid_data_loader  = create_train_dataloader(args)

    # ??????dataset
    # Create dataset, tokenizer and dataloader.
    train_ds, test_ds = load_dataset('TEDTalk', splits=('train', 'test'), lazy=False)
    label_list = train_ds.label_list
    label_num = len(label_list)

    # ?????????????????????  
    # Define the model netword and its loss
    model = ElectraForTokenClassification.from_pretrained(args.model_name_or_path, num_classes= label_num)

    # ??????AdamW?????????
    num_training_steps = args.max_steps if args.max_steps > 0 else len(train_data_loader) * args.num_train_epochs
    lr_scheduler = LinearDecayWithWarmup(float(args.learning_rate), num_training_steps, args.warmup_steps)

    # Generate parameter names needed to perform weight decay.
    # All bias and LayerNorm parameters are excluded.
    decay_params = [
            p.name for n, p in model.named_parameters()
            if not any(nd in n for nd in ["bias", "norm"])
        ]

    optimizer = paddle.optimizer.AdamW(
            learning_rate=lr_scheduler,
            epsilon=float(args.adam_epsilon),
            parameters=model.parameters(),
            weight_decay=args.weight_decay,
            apply_decay_param_fun=lambda x: x in decay_params)     

    # ?????????????????? - Cross Entropy  
    loss_fct = paddle.nn.loss.CrossEntropyLoss(ignore_index=args.ignore_label)

    # ??????????????????
    metric = paddle.metric.Accuracy()

    # ????????????
    do_train(args)
