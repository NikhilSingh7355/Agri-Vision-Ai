"""Train the AgriVision AI leaf-disease classifier (MobileNetV2 transfer learning).

Run on Google Colab (free GPU):  !pip install tensorflow-datasets scikit-learn && python train.py
Outputs: model.keras, labels.json, metrics.json  -> put them next to app.py.
"""
import json
import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

IMG, BATCH, SEED = 224, 64, 42
splits = ["train[:80%]", "train[80%:90%]", "train[90%:]"]
(train, val, test), info = tfds.load("plant_village", split=splits, as_supervised=True, with_info=True)
labels = info.features["label"].names
n = len(labels)


def prep(x, y):
    return tf.image.resize(x, (IMG, IMG)), y


def pipe(ds, shuffle=False):
    ds = ds.map(prep, num_parallel_calls=tf.data.AUTOTUNE)
    if shuffle:
        ds = ds.shuffle(2000, seed=SEED)
    return ds.batch(BATCH).prefetch(tf.data.AUTOTUNE)


train_ds, val_ds, test_ds = pipe(train, True), pipe(val), pipe(test)

aug = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal_and_vertical"),
    tf.keras.layers.RandomRotation(0.15),
    tf.keras.layers.RandomZoom(0.15),
    tf.keras.layers.RandomBrightness(0.2),
])
base = tf.keras.applications.MobileNetV2(input_shape=(IMG, IMG, 3), include_top=False, weights="imagenet")
base.trainable = False

inp = tf.keras.Input((IMG, IMG, 3))
x = aug(inp)
x = tf.keras.applications.mobilenet_v2.preprocess_input(x)   # model takes raw 0-255 pixels
x = base(x, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.3)(x)
out = tf.keras.layers.Dense(n, activation="softmax")(x)
model = tf.keras.Model(inp, out)

model.compile(tf.keras.optimizers.Adam(1e-3), "sparse_categorical_crossentropy", ["accuracy"])
model.fit(train_ds, validation_data=val_ds, epochs=4)

base.trainable = True
for layer in base.layers[:-30]:
    layer.trainable = False
model.compile(tf.keras.optimizers.Adam(1e-5), "sparse_categorical_crossentropy", ["accuracy"])
model.fit(train_ds, validation_data=val_ds, epochs=3)

y_true = np.concatenate([y.numpy() for _, y in test_ds])
y_pred = np.argmax(model.predict(test_ds), axis=1)
p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
metrics = dict(accuracy=float(accuracy_score(y_true, y_pred)), precision=float(p), recall=float(r), f1=float(f))
print(classification_report(y_true, y_pred, target_names=labels, zero_division=0))
print(metrics)

model.save("model.keras")
json.dump(labels, open("labels.json", "w"))
json.dump(metrics, open("metrics.json", "w"))
