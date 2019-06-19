from pydub import AudioSegment
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.offline as offline
import os
import shutil
import json
from pydub.silence import split_on_silence

import IBM_STT


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


def split_on_silence_pyduf(sound, min_silence_len=1500, silence_thresh=30, keep_silence=500):
    chunks = split_on_silence(
        sound,
        # 1500ms以上の無音がある箇所で分割
        min_silence_len=min_silence_len,
        # -30dBFS以下で無音とみなす
        silence_thresh=-silence_thresh,
        # 分割後500msだけ、無音を残す
        keep_silence=keep_silence
    )
    # 分割数の表示
    print('split: ', len(chunks), ' chunk')
    return chunks


class ActiveSoundDetection:
    def __init__(self, sound):
        self.sound = sound

        # 情報の取得
        self.time = self.sound.duration_seconds  # 再生時間(秒)
        self.rate = self.sound.frame_rate  # サンプリングレート(Hz)
        self.channel = self.sound.channels  # チャンネル数(1:mono, 2:stereo)

        # 情報の表示
        print('チャンネル数：', self.channel)
        print('サンプリングレート：', self.rate)
        print('再生時間：', self.time)

        # NumPy配列に返還
        self.data = np.array(self.sound.get_array_of_samples())
        print(self.data.shape)

        self.split_sound = {}
        self.window = 1

    def split_on_silence_orig(self, split_len=1000, silence_thresh=1000):
        # 前処理
        time = int(self.time)
        self.data = self.data[:self.rate * time]

        # 振幅計算
        self.window = int(self.rate / (1000 / split_len))
        w_maxes = window_max(self.data, self.window)
        w_mines = window_min(self.data, self.window)
        w_width = w_maxes - w_mines
        # print(w_width)

        # 信号のon/off判定
        data_bool = np.where(w_width < silence_thresh, 0, 1)
        flg = np.diff(data_bool)
        if flg[0] == 0 and data_bool[0] == 1:  # 開始時点から有声区間だった時
            flg = np.insert(flg, 0, 1)

        # 区間計算
        np_on = np.where(flg == 1)[0]
        np_off = np.where(flg == -1)[0] + 1
        if len(np_on) > len(np_off):  # 終了時点まで有声区間だった時
            np_off = np.append(np_off, len(flg))
        sections = np.stack([np_on, np_off], axis=1) * split_len
        # print(sections)

        chunks = []
        for section in sections:
            chunks.append(self.sound[section[0]: section[1]])
        print('split: ', len(chunks), ' chunk')

        self.split_sound['chunks'] = chunks
        self.split_sound['sections'] = sections

    def save_splits(self, target_dir, clear_dir=True):
        if clear_dir:
            shutil.rmtree(target_dir)
            os.mkdir(target_dir)

        chunks = self.split_sound['chunks']
        for i, chunk in enumerate(chunks):
            chunk.export(target_dir + str(i) + '.mp3', format='mp3')

    def plot_raw_sound(self):
        x = np.arange(self.data.size) / self.window
        trace0 = go.Scatter(x=x, y=self.data, mode='lines', name='X')
        fig = dict(data=[trace0])
        offline.plot(fig, filename='plotly_out/sample.html')


def callback_fn(texts):
    for text in texts:
        data = {
            "meta": {
                "type": "speechText"
            },
            "data": {
                "text": text,
                "isInterrupt": False
            }
        }
        body = json.dumps(data, ensure_ascii=False)
        print(body)


def init():
    # 音声ファイルの読み込み
    # sound = AudioSegment.from_file("reproduction-smp-edited.wav", "wav")
    sound = AudioSegment.from_mp3('sound_data/movie1.mp3')

    asd = ActiveSoundDetection(sound)
    asd.split_on_silence_orig(split_len=1500, silence_thresh=1000)
    target_dir = 'sound_data/temp/'
    asd.save_splits(target_dir, clear_dir=True)

    for i in range(len(asd.split_sound['chunks'])):
        ibm_stt = IBM_STT.IBM_STT(target_dir + str(i) + '.mp3', callback_fn)
        ibm_stt.stt(target_dir='stt_results/movie1/')


if __name__ == '__main__':
    init()
