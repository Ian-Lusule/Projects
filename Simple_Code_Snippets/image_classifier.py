import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50V2, InceptionV3, EfficientNetB0
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np
import matplotlib.pyplot as plt
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 1. Data Loading and Preprocessing
def load_and_preprocess_data(dataset_name='cifar10', img_size=(32, 32), batch_size=32, validation_split=0.2):
    logging.info(f"Loading {dataset_name} dataset...")
    if dataset_name == 'cifar10':
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
    elif dataset_name == 'mnist':
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
        # Reshape MNIST images to have a channel dimension
        x_train = x_train.reshape(-1, 28, 28, 1)
        x_test = x_test.reshape(-1, 28, 28, 1)
        img_size = (28, 28)
    else:
        raise ValueError(f"Dataset {dataset_name} not supported.")
    
    logging.info("Data loaded successfully.")

    # Normalize pixel values to be between 0 and 1
    x_train = x_train.astype('float32') / 255.0
    x_test = x_test.astype('float32') / 255.0

    # Convert labels to one-hot encoding
    num_classes = len(np.unique(y_train))
    y_train = tf.keras.utils.to_categorical(y_train, num_classes)
    y_test = tf.keras.utils.to_categorical(y_test, num_classes)
    
    # Split training data into training and validation sets
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=validation_split, random_state=42)
    
    logging.info("Data preprocessed and split into training, validation, and testing sets.")
    return x_train, y_train, x_val, y_val, x_test, y_test, num_classes, img_size

# 2. Data Augmentation
def create_data_augmentation(rotation_range=20, width_shift_range=0.2, height_shift_range=0.2, horizontal_flip=True):
    datagen = ImageDataGenerator(
        rotation_range=rotation_range,
        width_shift_range=width_shift_range,
        height_shift_range=height_shift_range,
        horizontal_flip=horizontal_flip
    )
    logging.info("Data augmentation generator created.")
    return datagen

# 3. Model Building
def create_model(model_name='resnet50v2', num_classes=10, img_size=(32, 32)):
    logging.info(f"Creating {model_name} model...")
    if model_name == 'resnet50v2':
        base_model = ResNet50V2(include_top=False, weights='imagenet', input_shape=img_size + (3,))
    elif model_name == 'inceptionv3':
        base_model = InceptionV3(include_top=False, weights='imagenet', input_shape=img_size + (3,))
    elif model_name == 'efficientnetb0':
        base_model = EfficientNetB0(include_top=False, weights='imagenet', input_shape=img_size + (3,))
    else:
        raise ValueError(f"Model {model_name} not supported.")

    # Freeze the layers of the pre-trained model
    for layer in base_model.layers:
        layer.trainable = False

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])
    logging.info(f"{model_name} model created.")
    return model

# 4. Model Training
def train_model(model, x_train, y_train, x_val, y_val, data_augmentation, epochs=10, batch_size=32, learning_rate=0.001):
    logging.info("Starting model training...")
    model.compile(optimizer=optimizers.Adam(learning_rate=learning_rate),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    if data_augmentation is not None:
        data_augmentation.fit(x_train)
        history = model.fit(data_augmentation.flow(x_train, y_train, batch_size=batch_size),
                              epochs=epochs,
                              validation_data=(x_val, y_val))
    else:
        history = model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(x_val, y_val))

    logging.info("Model training complete.")
    return history

# 5. Model Evaluation
def evaluate_model(model, x_test, y_test):
    logging.info("Evaluating model...")
    loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
    logging.info(f"Test Loss: {loss}")
    logging.info(f"Test Accuracy: {accuracy}")

    y_pred = model.predict(x_test)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true = np.argmax(y_test, axis=1)
    print(classification_report(y_true, y_pred_classes))
    logging.info("Model evaluation complete.")

# 6. Hyperparameter Optimization (Simple Example - Grid Search)
def hyperparameter_tuning(x_train, y_train, x_val, y_val, img_size, num_classes):
    logging.info("Starting hyperparameter tuning (grid search example)...")
    best_accuracy = 0.0
    best_params = {}
    
    learning_rates = [0.001, 0.0001]
    epochs = [5, 10]
    
    for lr in learning_rates:
        for ep in epochs:
            logging.info(f"Trying learning rate: {lr}, epochs: {ep}")
            
            model = create_model(num_classes=num_classes, img_size=img_size)  # Assuming a default model
            history = train_model(model, x_train, y_train, x_val, y_val, None, epochs=ep, learning_rate=lr)
            
            _, accuracy = model.evaluate(x_val, y_val, verbose=0)
            logging.info(f"Validation Accuracy: {accuracy}")
            
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_params = {'learning_rate': lr, 'epochs': ep}
    
    logging.info(f"Best hyperparameters: {best_params}, Best Validation Accuracy: {best_accuracy}")
    return best_params

# 7. Model Saving
def save_model(model, model_path='image_classifier_model.h5'):
    logging.info(f"Saving model to {model_path}...")
    model.save(model_path)
    logging.info("Model saved.")

# 8. Model Loading
def load_model(model_path='image_classifier_model.h5'):
    logging.info(f"Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path)
    logging.info("Model loaded.")
    return model

# Example Usage
if __name__ == '__main__':
    
    # Configuration
    DATASET_NAME = 'cifar10'  # Or 'mnist'
    IMG_SIZE = (32, 32) if DATASET_NAME == 'cifar10' else (28, 28)
    BATCH_SIZE = 32
    EPOCHS = 10
    LEARNING_RATE = 0.001
    MODEL_NAME = 'resnet50v2' # Or 'inceptionv3', 'efficientnetb0'
    MODEL_PATH = 'image_classifier_model.h5'
    
    # 1. Load and Preprocess Data
    x_train, y_train, x_val, y_val, x_test, y_test, num_classes, img_size = load_and_preprocess_data(DATASET_NAME, IMG_SIZE, BATCH_SIZE)

    # 2. Data Augmentation
    data_augmentation = create_data_augmentation()

    # 3. Hyperparameter Tuning (Optional)
    # best_params = hyperparameter_tuning(x_train, y_train, x_val, y_val, img_size, num_classes)
    # LEARNING_RATE = best_params.get('learning_rate', LEARNING_RATE)
    # EPOCHS = best_params.get('epochs', EPOCHS)

    # 4. Create Model
    model = create_model(MODEL_NAME, num_classes, img_size)

    # 5. Train Model
    history = train_model(model, x_train, y_train, x_val, y_val, data_augmentation, EPOCHS, BATCH_SIZE, LEARNING_RATE)

    # 6. Evaluate Model
    evaluate_model(model, x_test, y_test)

    # 7. Save Model
    save_model(model, MODEL_PATH)

    # 8. Load Model and Predict (Example)
    loaded_model = load_model(MODEL_PATH)
    # Example prediction using the loaded model
    sample_image = x_test[0].reshape(1, img_size[0], img_size[1], x_test.shape[-1])
    prediction = loaded_model.predict(sample_image)
    predicted_class = np.argmax(prediction, axis=1)[0]
    print(f"Predicted class for sample image: {predicted_class}")