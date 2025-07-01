import os
import tensorflow as tf
import shutil
import rarfile
import os
import shutil

# Directorio base donde se encuentran las carpetas de clases
BASE_DIR = 'C:/Users/Administrador/Downloads/mie'  # Ajusta la ruta a tu directorio

# 1) Directorio destino donde copiarás las imágenes
DST_ROOT = os.path.join(BASE_DIR, 'dataset')

# 2) Límite de imágenes por clase
LIMIT_PER_CLASS = 960

# 3) Encuentra todas las carpetas de clases dentro del directorio BASE_DIR
all_dirs = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
print("Clases detectadas:", all_dirs)

# 4) Crear la carpeta dataset y las subcarpetas para cada clase
os.makedirs(DST_ROOT, exist_ok=True)

# Para cada clase, crear una subcarpeta en 'dataset' y copiar las imágenes
for cls in all_dirs:
    src_dir = os.path.join(BASE_DIR, cls)
    dst_dir = os.path.join(DST_ROOT, cls)
    
    # Crear la subcarpeta para la clase si no existe
    os.makedirs(dst_dir, exist_ok=True)

    # Listar los archivos de la clase (solo archivos de imagen)
    files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f)) and not f.startswith('.')]
    
    # Copiar hasta LIMIT_PER_CLASS imágenes
    to_copy = files[:LIMIT_PER_CLASS]

    for fname in to_copy:
        shutil.copy(os.path.join(src_dir, fname), os.path.join(dst_dir, fname))
    
    print(f"✅ Clase '{cls}': copiadas {len(to_copy)} imágenes a '{dst_dir}'")

# Resumen final de lo copiado
print("\n🌟 Estructura final en 'dataset/':")
for cls in all_dirs:
    count = len(os.listdir(os.path.join(DST_ROOT, cls)))
    print(f"  └── {cls}/ ({count} imágenes)")


# **Cargar imágenes y crear los datasets de entrenamiento y validación**
raw_train_ds = tf.keras.utils.image_dataset_from_directory(
    BASE_DIR,
    validation_split=0.2,
    subset='training',
    seed=42,
    image_size=(224, 224),
    batch_size=32
)
print("Clases detectadas:", raw_train_ds.class_names)

raw_val_ds = tf.keras.utils.image_dataset_from_directory(
    BASE_DIR,
    validation_split=0.2,
    subset='validation',
    seed=42,
    image_size=(224, 224),
    batch_size=32
)

# 3) Normalización sin aumento de datos
normalization = tf.keras.layers.Rescaling(1./255)

train_ds = raw_train_ds \
    .map(lambda x, y: (normalization(x), y), tf.data.AUTOTUNE) \
    .shuffle(1000) \
    .prefetch(tf.data.AUTOTUNE)

val_ds = raw_val_ds \
    .map(lambda x, y: (normalization(x), y), tf.data.AUTOTUNE) \
    .cache() \
    .prefetch(tf.data.AUTOTUNE)


# **Crear el modelo de clasificación utilizando MobileNetV2**
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet',
    pooling='avg'
)
base_model.trainable = False  # congelamos el backbone

# Tu “cabeza” de clasificación con 6 salidas
num_classes = len(raw_train_ds.class_names)  # debería ser 6
model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# Entrenamiento del modelo
EPOCHS = 40  # Ajusta el número de épocas a tus necesidades

history = model.fit(
    train_ds,               # Dataset de entrenamiento
    epochs=EPOCHS,          # Número de épocas
    validation_data=val_ds, # Dataset de validación
    verbose=1               # Mostrar el progreso del entrenamiento
)


# **Graficar la precisión y la pérdida**
import matplotlib.pyplot as plt

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

num_epochs = len(acc)
epochs_range = range(num_epochs)

plt.figure(figsize=(8,8))

plt.subplot(1,2,1)
plt.plot(epochs_range, acc, label='Precisión Entrenamiento')
plt.plot(epochs_range, val_acc, label='Precisión Validación')
plt.legend(loc='lower right')
plt.title('Precisión Entrenamiento y Validación')

plt.subplot(1,2,2)
plt.plot(epochs_range, loss, label='Pérdida Entrenamiento')
plt.plot(epochs_range, val_loss, label='Pérdida Validación')
plt.legend(loc='upper right')
plt.title('Pérdida Entrenamiento y Validación')

plt.tight_layout()
plt.show()


# **Guardar y exportar el modelo entrenado**
os.makedirs("modelo_cocina/1", exist_ok=True)

# Guarda el modelo en formato .h5
model.save('modelo_cocina/1/modelo_entrenado.h5')
print("✅ Modelo guardado en 'modelo_cocina/1/modelo_entrenado.h5'")

# Exporta el modelo en formato SavedModel para servir en producción
model.save('modelo_cocina/1/saved_model')
print("✅ Modelo exportado en formato SavedModel en 'modelo_cocina/1/saved_model'")

# Comprimir el modelo guardado
shutil.make_archive('modelo_cocina/1', 'zip', 'modelo_cocina/1')
print("✅ Modelo comprimido como 'modelo_cocina/1.zip'")
