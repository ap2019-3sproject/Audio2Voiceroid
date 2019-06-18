from pydub import AudioSegment
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.offline as offline


def window_comm(X, window):
    n = int(X.size / window)
    X = X[:n * window]
    return np.reshape(X, (n, window))


def window_min(X, window):
    X = window_comm(X, window)
    return np.min(X, axis=1)


def window_max(X, window):
    X = window_comm(X, window)
    return np.max(X, axis=1)


def init():
    # 音声ファイルの読み込み
    # sound = AudioSegment.from_file("reproduction-smp-edited.wav", "wav")
    sound = AudioSegment.from_mp3('sound_data/sample_08.mp3')

    # 情報の取得
    time = sound.duration_seconds  # 再生時間(秒)
    rate = sound.frame_rate  # サンプリングレート(Hz)
    channel = sound.channels  # チャンネル数(1:mono, 2:stereo)

    # 情報の表示
    print('チャンネル数：', channel)
    print('サンプリングレート：', rate)
    print('再生時間：', time)

    # NumPy配列に返還
    data = np.array(sound.get_array_of_samples())
    print(data.shape)

    # 前処理
    time = int(time)
    data = data[:rate * time]

    window = int(rate)
    w_maxes = window_max(data, window)
    w_mines = window_min(data, window)
    w_width = w_maxes - w_mines
    print(w_width)

    # x = np.arange(data.size) / window
    # trace0 = go.Scatter(x=x, y=data, mode='lines', name='X')
    # fig = dict(data=[trace0])
    # offline.plot(fig, filename='plotly_out/sample.html')


if __name__ == '__main__':
    init()
