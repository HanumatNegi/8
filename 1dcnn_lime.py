# -*- coding: utf-8 -*-
"""1DCNN-Lime.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1xwk4Dwm_Oa7ETxP8ZUdNP828w2VA8EJy
"""

!pip install shap

!pip install interpret

# Install the scikeras library

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler,LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, accuracy_score, precision_score
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import classification_report
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout
from tensorflow import keras
from tensorflow.keras import layers

"""## **importing dataset**"""

from google.colab import drive
drive.mount('/content/drive')

dataset= '/content/drive/MyDrive/MalGAN/Datasets'

import os
print(os.listdir(dataset))

# Paths to the datasets
train_path = os.path.join(dataset, '8_family_training.csv')
test_path = os.path.join(dataset, '8_family_testing.csv')
validation_path = os.path.join(dataset, '8_family_validation.csv')

data_train = pd.read_csv(train_path)
data_test = pd.read_csv(test_path)
data_validation = pd.read_csv(validation_path)

data_train.head()

count=data_train['Malware'].value_counts()
print(count)

count_test=data_test['Malware'].value_counts()
print(count_test)

count_validation=data_validation['Malware'].value_counts()
print(count_validation)

X_train=data_train.drop(['Malware'],axis=1)
y_trian=data_train['Malware']

X_test=data_test.drop(['Malware'],axis=1)
y_test=data_test['Malware']

X_validation=data_validation.drop(['Malware'],axis=1)
y_validation=data_validation['Malware']

print(X_train.shape);
print(X_test.shape);
print(X_validation.shape);

X_train.head()

"""## **Preprocessing**"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder

lable = LabelEncoder()


for i in X_train.columns:
  if X_train[i].dtype == 'object':
    X_train[i] = lable.fit_transform(X_train[i])

X_train.head()

feature_names = list(X_train.columns)

for j in X_test.columns:
  if X_test[j].dtype == 'object':
    X_test[j] = lable.fit_transform(X_test[j])

for k in X_validation.columns:
  if X_validation[k].dtype == 'object':
    X_validation[k] = lable.fit_transform(X_validation[k])

y_train=lable.fit_transform(y_trian)
y_test=lable.fit_transform(y_test)
y_validation=lable.fit_transform(y_validation)

label_mapping_train = dict(zip(range(len(lable.classes_)), lable.classes_))


# Display the mapping
print("Label Mapping:", label_mapping_train)

class_name=['Benign', 'banbra', 'emotet', 'fareit', 'gozi', 'qbot', 'shade', 'tofsee', 'ursnif']

stdScale=StandardScaler()
X_train=stdScale.fit_transform(X_train)
X_test=stdScale.fit_transform(X_test)
X_validation=stdScale.fit_transform(X_validation)

X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_validation = X_validation.reshape(X_validation.shape[0], X_validation.shape[1], 1)

"""## **1DCNN**"""

def CNN(filters=32, kernel_size=3, activation='relu', optimizer='adam', Dropout=0.5):
    model = keras.Sequential()
    model.add(layers.Conv1D(filters=filters, kernel_size=kernel_size, activation=activation, input_shape=(X_train.shape[1], 1)))
    model.add(layers.MaxPooling1D(pool_size=2))
    model.add(layers.Conv1D(filters=64, kernel_size=kernel_size, activation=activation))
    model.add(layers.MaxPooling1D(pool_size=2))
    model.add(layers.Flatten())
    model.add(layers.Dropout(Dropout))
    model.add(layers.Dense(128, activation=activation))
    model.add(layers.Dense(9, activation='softmax'))  # Adjust based on number of classes

    model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

"""##**Parameters value for best accuracy:-**

Best Filters: 128

Best Kernel Size: 3

Best Dropout Rate: 0.4

Best Activation: relu

Best Optimizer: adam
"""

CNN_model=CNN(filters=128,
    kernel_size=3,
    Dropout=0.4,
    activation='relu',
    optimizer='adam')
Train=CNN_model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_validation, y_validation))

val_accuracy = CNN_model.evaluate(X_validation, y_validation)
print("Validation accuracy=", val_accuracy)

"""# **Testing**"""

def predict_fn(X):
    # Reshape X to match the expected input shape of your CNN model
    X = X.reshape(-1, 6006, 1)  # Reshape to (number of samples, 6006, 1)
    return CNN_model.predict(X)

y_pred=predict_fn(X_test)

y_pred=np.argmax(y_pred,axis=1)

y_pred=y_pred.reshape(-1,1)

accuracy_before_tuining=accuracy_score(y_test,y_pred)
print(f'Accuracy before tuning: {accuracy_before_tuining}')

report=classification_report(y_test,y_pred)
print(report)

# prompt: plot learning curve

import matplotlib.pyplot as plt

plt.plot(Train.history['accuracy'])
plt.plot(Train.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()

plt.plot(Train.history['loss'])
plt.plot(Train.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()

plt.scatter(range(len(y_test)), y_test, color='blue', label='Actual')

plt.scatter(range(len(y_pred)), y_pred, color='red', label='Predicted')

plt.xlabel('Data Point Index/X-axis')
plt.ylabel('Values')
plt.title('Actual vs Predicted Values')
plt.legend()
plt.show()

print(y_pred[100])

"""0: 'Benign', 1: 'banbra', 2: 'emotet', 3: 'fareit', 4: 'gozi', 5: 'qbot', 6: 'shade', 7: 'tofsee', 8: 'ursnif'"""

y_pred_labels_1 = []

for i in range(len(y_test)):
  if y_pred[i] == 0:
    y_pred_labels_1.append('Benign')
  elif y_pred[i] == 1:
    y_pred_labels_1.append('banbra')
  elif y_pred[i] == 2:
    y_pred_labels_1.append('emotet')
  elif y_pred[i] == 3:
    y_pred_labels_1.append('fareit')
  elif y_pred[i] == 4:
    y_pred_labels_1.append('gozi')
  elif y_pred[i] == 5:
    y_pred_labels_1.append('qbot')
  elif y_pred[i] == 6:
    y_pred_labels_1.append('shade')
  elif y_pred[i] == 7:
    y_pred_labels_1.append('tofsee')
  elif y_pred[i] == 8:
    y_pred_labels_1.append('ursnif')

print(y_pred_labels_1)

y_test_labels = []

for i in range(len(y_test)):
  if y_pred[i] == 0:
    y_test_labels.append('Benign')
  elif y_test[i] == 1:
    y_test_labels.append('banbra')
  elif y_test[i] == 2:
    y_test_labels.append('emotet')
  elif y_test[i] == 3:
    y_test_labels.append('fareit')
  elif y_test[i] == 4:
    y_test_labels.append('gozi')
  elif y_test[i] == 5:
    y_test_labels.append('qbot')
  elif y_test[i] == 6:
    y_test_labels.append('shade')
  elif y_test[i] == 7:
    y_test_labels.append('tofsee')
  elif y_test[i] == 8:
    y_test_labels.append('ursnif')


#print(y_pred_labels)

Output_before_tuining=pd.DataFrame({'Predicted':y_pred_labels_1})
Test_labels=pd.DataFrame({'Actual':y_test_labels})

print(Test_labels['Actual'].value_counts())

print(Output_before_tuining['Predicted'].value_counts())

"""## **Classification Conusion Matrix**"""

from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt="d", cmap="magma", xticklabels=label_mapping_train.values(), yticklabels=label_mapping_train.values())
plt.xlabel("Predicted Labels")
plt.ylabel("True Labels")
plt.title("Confusion Matrix with Class Labels")
plt.show()

"""# **Lime**"""

!pip install lime

from interpret.blackbox import LimeTabular

from lime.lime_tabular import LimeTabularExplainer

# Convert X_train to a NumPy array if it's a pandas DataFrame
if isinstance(X_train, pd.DataFrame):
    X_train = X_train.to_numpy()

# Reshape X_train to 2D if necessary
if X_train.ndim != 2:
    X_train = X_train.reshape(X_train.shape[0], -1)
    # Reshape to (number of samples, total number of features)

explainer = LimeTabularExplainer(
    training_data=X_train,
    feature_names=feature_names,
    class_names=class_name,
    mode="classification"
)

for i in range(30,50):
    # Change the instance
    exp = explainer.explain_instance(
        data_row=X_test[i].reshape(-1),
        predict_fn=predict_fn,
        num_features=10
    )

    print(f"Explanation for instance {i}:")
    exp.show_in_notebook(show_table=True)

noteshade=[]
for i in range (0,100):
  if y_pred_labels_1[i] !='shade':
    noteshade.append(i)

print(noteshade)

for i in range(0,100):
    # Change the instance
    exp = explainer.explain_instance(
        data_row=X_test[i].reshape(-1),
        predict_fn=predict_fn,
        num_features=10
    )

    print(f"Explanation for instance {i}:")
    exp.show_in_notebook(show_table=True)