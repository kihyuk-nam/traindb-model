"""
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import json
import os
from TrainDBBaseModelRunner import TrainDBModelRunner

class TrainDBCliModelRunner(TrainDBModelRunner):

  def train_model(self, modeltype_class, modeltype_path, real_data, table_metadata, model_path):
    model, train_info = super()._train(modeltype_class, modeltype_path, real_data, table_metadata, args, kwargs)
    model.save(model_path)
    return json.dumps(train_info)

  def generate_synopsis(self, modeltype_class, modeltype_path, model_path, row_count):
    syn_data = super()._synthesize(modeltype_class, modeltype_path, model_path, row_count)
    return syn_data

  def infer(self, modeltype_class, modeltype_path, model_path, agg_expr, group_by_column, where_condition):
    infer_results = super()._infer(modeltype_class, modeltype_path, model_path, agg_expr, group_by_column, where_condition)
    return infer_results

  def list_hyperparameters(self, modeltype_class, modeltype_path):
    hyperparams_info = super()._hyperparams(modeltype_class, modeltype_path)
    return json.dumps(hyperparams_info)

import argparse
import pandas as pd
import json
import sys
import csv

root_parser = argparse.ArgumentParser(description='TrainDB CLI Model Runner')
subparsers = root_parser.add_subparsers(dest='cmd')
parser_train = subparsers.add_parser('train', help='train model command')
parser_train.add_argument('modeltype_class', type=str, help='(str) modeltype class name')
parser_train.add_argument('modeltype_uri', type=str, help='(str) path for local model, or uri for remote model')
parser_train.add_argument('data_file', type=str, help='(str) path to .csv data file')
parser_train.add_argument('metadata_file', type=str, help='(str) path to .json table metadata file')
parser_train.add_argument('model_path', type=str, help='(str) path to model')

parser_synopsis = subparsers.add_parser('synopsis', help='generate synopsis command')
parser_synopsis.add_argument('modeltype_class', type=str, help='(str) modeltype class name')
parser_synopsis.add_argument('modeltype_uri', type=str, help='(str) path for local model, or uri for remote model')
parser_synopsis.add_argument('model_path', type=str, help='(str) path to model')
parser_synopsis.add_argument('row_count', type=int, help='(int) the number of rows to generate')
parser_synopsis.add_argument('output_file', type=str, help='(str) path to save generated synopsis file')

parser_synopsis = subparsers.add_parser('infer', help='inference model command')
parser_synopsis.add_argument('modeltype_class', type=str, help='(str) modeltype class name')
parser_synopsis.add_argument('modeltype_uri', type=str, help='(str) path for local model, or uri for remote model')
parser_synopsis.add_argument('model_path', type=str, help='(str) path to model')
parser_synopsis.add_argument('agg_expr', type=str, help='(str) aggregation expression')
parser_synopsis.add_argument('group_by_column', type=str, help='(str) column specified in GROUP BY clause')
parser_synopsis.add_argument('where_condition', type=str, help='(str) filter condition specified in WHERE clause')
parser_synopsis.add_argument('output_file', type=str, nargs='?', default='', help='(str) path to save inferred query result file')

parser_train = subparsers.add_parser('list', help='list model hyperparameters')
parser_train.add_argument('modeltype_class', type=str, help='(str) modeltype class name')
parser_train.add_argument('modeltype_uri', type=str, help='(str) path for local model, or uri for remote model')
parser_train.add_argument('output_file', type=str, help='(str) path to .json model hyperparameters file')

args = root_parser.parse_args()
runner = TrainDBCliModelRunner()
if args.cmd == 'train':
  data_file = pd.read_csv(args.data_file)
  with open(args.metadata_file) as metadata_file:
    table_metadata = json.load(metadata_file)
  json_train_info = runner.train_model(args.modeltype_class, args.modeltype_uri, data_file, table_metadata, args.model_path)
  with open(os.path.join(args.model_path, 'train_info.json'), 'w') as f:
    f.write(json_train_info)
  sys.exit(0)
elif args.cmd == 'synopsis':
  syn_data = runner.generate_synopsis(args.modeltype_class, args.modeltype_uri, args.model_path, args.row_count)
  syn_data.to_csv(args.output_file, index=False)
  sys.exit(0)
elif args.cmd == 'infer':
  aqp_result, confidence_interval = runner.infer(args.modeltype_class, args.modeltype_uri, args.model_path, args.agg_expr, args.group_by_column, args.where_condition)
  if args.output_file == '':
    print(aqp_result)
  else:
    with open(args.output_file, 'w') as f:
      writer = csv.writer(f)
      writer.writerows(aqp_result)
  sys.exit(0)
elif args.cmd == 'list':
  json_hyperparams_info = runner.list_hyperparameters(args.modeltype_class, args.modeltype_uri)
  with open(args.output_file, 'w') as f:
    f.write(json_hyperparams_info)
  sys.exit(0)
else:
  root_parser.print_help()
