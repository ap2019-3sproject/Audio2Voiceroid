import subprocess
import os


class VideoConverter:
    def __init__(self, filepath):
        self.filepath = filepath
        basename = os.path.basename(self.filepath)
        self.filename, self.fileext = os.path.splitext(basename)  # ファイル名と拡張子に分離

        # ffmpegのディレクトリを格納
        command = ['which', 'ffmpeg']
        res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.ffmpeg_dir = res.stdout.decode('utf8')[:-len(os.linesep)]  # 改行文字削除
        print(self.ffmpeg_dir)

    # 音声ファイル抽出
    def convert_to_audio(self, ext='wav', target_dir='sound_data/'):
        save_file = target_dir + self.filename + '.' + ext
        command = [self.ffmpeg_dir, '-y', '-i', self.filepath, save_file]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return save_file

    # 動画の音声削除
    def convert_to_silence_video(self, target_dir='video_data/'):
        save_file = target_dir + self.filename + self.fileext
        command = [self.ffmpeg_dir, '-y', '-i', self.filepath, '-vcodec', 'copy', '-an', save_file]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return save_file


def init():
    converter = VideoConverter('動画までの絶対パス')
    audio_file = converter.convert_to_audio()
    print(audio_file)
    # video_file = converter.convert_to_silence_video()
    # print(video_file)


if __name__ == '__main__':
    init()
