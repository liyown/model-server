from io import BytesIO


def bytesIO_to_audio_sequence(audio: BytesIO, sr=None):
    """BytesIO 转音频序列
    :param audio: BytesIO 对象
    """
    audio.seek(0)
    audio_data = audio.read()
    audio_sequence, sample_rate = librosa.load(audio_data, sr=None)
    return audio_sequence, sample_rate