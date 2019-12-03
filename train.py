import sys
import copy, time
import itertools
import os
import shutil
import sys
from inspect import getsourcefile

import tensorflow as tf
import numpy as np
from ConvLSTM import ConvLSTM

# raw_input returns the empty string for "enter"
yes = {'y'}
no = {'n'}

reset = False  # Clear all learned models
sys.stdout.write('Do you want to reset training process? "y" or "n": ')
choice = raw_input().lower()
if choice in yes:
    reset = True
elif choice in no:
    reset = False
else:
    sys.stdout.write("Please respond with 'y' or 'n'")

current_path = os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
import_path = os.path.abspath(os.path.join(current_path, "../.."))

if import_path not in sys.path:
    sys.path.append(import_path)

# tensorboard --logdir=/media/newhd/Ha/my_env/cell_2/model/summary

# PROJECT_DIR = '/Users/phanha/Google Drive/Work/PyCharm/el_2.1'
PROJECT_DIR = '/media/newhd/Ha/my_env/cell_2'

MODEL_DIR = os.path.join(PROJECT_DIR, "model")
CHECKPOINT_DIR = os.path.join(MODEL_DIR, "checkpoints")
SUMMARY_DIR = os.path.join(MODEL_DIR, "summary")

latest_checkpoint = tf.train.latest_checkpoint(CHECKPOINT_DIR)

# Optionally empty model directory
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)
if reset:  # and latest_checkpoint is None:
    shutil.rmtree(CHECKPOINT_DIR, ignore_errors=True)
    shutil.rmtree(SUMMARY_DIR, ignore_errors=True)
    latest_checkpoint = None

if not os.path.exists(CHECKPOINT_DIR):
    os.makedirs(CHECKPOINT_DIR)

if not os.path.exists(SUMMARY_DIR):
    os.makedirs(SUMMARY_DIR)

summary_writer = tf.summary.FileWriter(SUMMARY_DIR)

# optimizer = tf.train.AdamOptimizer(FLAGS.learning_rate)
optimizer = tf.train.RMSPropOptimizer(learning_rate=5e-4)

config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.9
sess = tf.Session(config=config)
# sess = tf.InteractiveSession()

# Get data
data = np.load('/media/newhd/Ha/data/BAEC/big/train.npz')
training_data = data['input_raw_data']
training_labels = data['output_raw_data']

saver = None

start_time = time.time()
model = ConvLSTM(sess, optimizer, saver, CHECKPOINT_DIR,
                 summary_writer=summary_writer,
                 training_data=training_data,
                 training_labels=training_labels)
sess.run(tf.global_variables_initializer())
duration = time.time() - start_time
print "%.2f" % duration, 'graph building time ---'

saver_variables = tf.global_variables()
saver = tf.train.Saver(var_list=saver_variables, max_to_keep=4)
model.saver = saver


if latest_checkpoint is not None:
    # Load a previous checkpoint if it exists
    tf.reset_default_graph()
    imported_meta = tf.train.import_meta_graph(latest_checkpoint + ".meta")
    print("Loading model checkpoint: {}".format(latest_checkpoint))
    print tf.train.latest_checkpoint(CHECKPOINT_DIR), "tf.train.latest_checkpoint('./')"
    imported_meta.restore(sess, latest_checkpoint)

    if False:
        data = np.load('/media/newhd/Ha/data/BAEC/big/test.npz')
        model.test(data['input_raw_data'], data['output_raw_data'])
    else:
        model.run_train()
else:
    sess.graph.finalize()
    model.run_train()

