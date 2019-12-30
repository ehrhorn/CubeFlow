import tensorflow as tf

def cnn_model(config):
    model = tf.keras.models.Sequential()
    model.add(
        tf.keras.layers.Conv1D(
            filters=32,
            kernel_size=5,
            strides=2,
            padding='valid',
            data_format='channels_last',
            dilation_rate=1,
            activation=tf.keras.layers.LeakyReLU(),
            use_bias=True,
            kernel_initializer='glorot_uniform',
            bias_initializer='zeros',
            kernel_regularizer=None,
            bias_regularizer=None,
            activity_regularizer=None,
            kernel_constraint=None,
            bias_constraint=None,
            input_shape=(config.max_doms, len(config.features))
        )
    )
    model.add(
        tf.keras.layers.Conv1D(
            filters=64,
            kernel_size=5,
            strides=2,
            padding='valid',
            data_format='channels_last',
            dilation_rate=1,
            activation=tf.keras.layers.LeakyReLU(),
            use_bias=True,
            kernel_initializer='glorot_uniform',
            bias_initializer='zeros',
            kernel_regularizer=None,
            bias_regularizer=None,
            activity_regularizer=None,
            kernel_constraint=None,
            bias_constraint=None
        )
    )
    model.add(
        tf.keras.layers.Conv1D(
            filters=128,
            kernel_size=5,
            strides=2,
            padding='valid',
            data_format='channels_last',
            dilation_rate=1,
            activation=tf.keras.layers.LeakyReLU(),
            use_bias=True,
            kernel_initializer='glorot_uniform',
            bias_initializer='zeros',
            kernel_regularizer=None,
            bias_regularizer=None,
            activity_regularizer=None,
            kernel_constraint=None,
            bias_constraint=None
        )
    )
    model.add(
        tf.keras.layers.Conv1D(
            filters=256,
            kernel_size=5,
            strides=2,
            padding='valid',
            data_format='channels_last',
            dilation_rate=1,
            activation=tf.keras.layers.LeakyReLU(),
            use_bias=True,
            kernel_initializer='glorot_uniform',
            bias_initializer='zeros',
            kernel_regularizer=None,
            bias_regularizer=None,
            activity_regularizer=None,
            kernel_constraint=None,
            bias_constraint=None
        )
    )
    model.add(
        tf.keras.layers.Flatten(
            data_format='channels_last'
        )
    )
    model.add(
        tf.keras.layers.Dense(
            units=len(config.targets),
            activation=None,
            use_bias=True,
            kernel_initializer='glorot_uniform',
            bias_initializer='zeros',
            kernel_regularizer=None,
            bias_regularizer=None,
            activity_regularizer=None,
            kernel_constraint=None,
            bias_constraint=None
        )
    )
    return model
