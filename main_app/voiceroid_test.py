import IBM_STT
import ActiveSoundDetection
import Voiceroid

from pydub import AudioSegment
import os
import shutil
import numpy as np
import subprocess


def concat(target_dir, ext, num, silence):
    command = ['ffmpeg']
    command.append('-y')
    for i in range(num):
        command.append('-f')
        command.append('lavfi')
        command.append('-i')
        command.append('aevalsrc=0:d={}'.format(silence[i]))
        command.append('-i')
        command.append('{}.'.format(i) + ext)
    command.append('-filter_complex')
    option = ''
    for i in range(num):
        option += '[{}:0][{}:0]'.format(i*2, i*2+1)
    option += 'concat=n={}:v=0:a=1'.format(2*num)
    command.append(option)
    command.append('out.mp3')
    print(command)
    proc = subprocess.run(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, cwd=target_dir)
    print(proc.stdout)


def callback_fn(texts):
    global _voiceroid
    global _cnt
    _cnt += 1
    text_num = len(texts)
    for i in range(text_num):
        text = texts[i]
        params = {
            'volume': '1.3',
            'speed': '1.0',
            'pitch': '0.8',
            'intonation': '0.8',
            'save': '絶対パス/voiceroid_out/temp/' + str(_cnt) + '_' + str(i) + '.wav',
            't': text
        }
        _voiceroid.talk(params)
        print(text)
    combined = AudioSegment.empty()
    for i in range(text_num):
        sound = AudioSegment.from_wav('voiceroid_out/temp/' + str(_cnt) + '_' + str(i) + '.wav')
        combined += sound
    combined.export('voiceroid_out/temp/' + str(_cnt) + '.wav', format='wav')

    global _size
    if _cnt == _size:
        silences = [1] * text_num
        concat('voiceroid_out/temp/', 'wav', text_num, silences)


def init():
    
    shutil.rmtree('voiceroid_out/temp/')
    os.mkdir('voiceroid_out/temp/')

    # 音声ファイルの読み込み
    # sound = AudioSegment.from_file("reproduction-smp-edited.wav", "wav")
    sound = AudioSegment.from_mp3('sound_data/movie1.mp3')

    asd = ActiveSoundDetection.ActiveSoundDetection(sound)
    asd.split_on_silence_orig(split_len=1500, silence_thresh=1000)
    target_dir = 'sound_data/temp/'
    asd.save_splits(target_dir, clear_dir=True)

    np.savetxt(target_dir + 'sections.csv', asd.split_sound['sections'], delimiter=',')
    global _size
    _size = len(asd.split_sound['chunks'])
    for i in range(_size):
        ibm_stt = IBM_STT.IBM_STT(target_dir + str(i) + '.mp3', callback_fn)
        ibm_stt.stt(target_dir='stt_results/movie1/')


if __name__ == '__main__':
    _voiceroid = Voiceroid.Voiceroid(1700, 'seikasay.exe')
    _cnt = 0
    _size = 0
    init()