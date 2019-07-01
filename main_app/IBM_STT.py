import json
import os
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource


class IBM_STT:
    class MyRecognizeCallback(RecognizeCallback):
        def __init__(self, on_data_fn):
            RecognizeCallback.__init__(self)
            self.on_data_fn = on_data_fn

        def on_data(self, data):
            print(json.dumps(data, indent=2))
            self.on_data_fn(data)

        def on_error(self, error):
            print('Error received: {}'.format(error))

        def on_inactivity_timeout(self, error):
            print('Inactivity timeout: {}'.format(error))

    def __init__(self, filepath, callback_fn):
        self.key = ''
        self.url = ''
        self.filepath = filepath
        basename = os.path.basename(self.filepath)
        self.filename, self.fileext = os.path.splitext(basename)  # ファイル名と拡張子に分離
        self.result_json = {}
        self.result_texts = []
        self.load_key()  # api_key読込
        self.rCallback = self.MyRecognizeCallback(self.save_result)
        self.speech_to_text = SpeechToTextV1(
            iam_apikey=self.key,
            url=self.url
        )
        self.callback_fn = callback_fn

    def load_key(self):
        with open('api_key.json') as f:
            df = json.load(f)
            print(json.dumps(df, indent=2))
            self.key = df['apikey']
            self.url = df['url']

    def stt(self, target_dir='stt_results/'):
        print('\n--- START STT ---\n')
        result_filename = target_dir + self.filename + '.json'
        if os.path.exists(result_filename):
            print('ファイルあったのん！')
            with open(result_filename, encoding="utf-8") as f:
                df = json.load(f)
                self.set_result(df)
        else:
            with open(self.filepath, 'rb') as audio_file:
                audio_source = AudioSource(audio_file)
                self.speech_to_text.recognize_using_websocket(
                    audio=audio_source,
                    content_type='audio/' + self.fileext[1:],  # 拡張子前の '.' 除去
                    recognize_callback=self.rCallback,
                    model='ja-JP_BroadbandModel',
                    max_alternatives=1)

    def save_result(self, data):
        result_filename = 'stt_results/' + self.filename + '.json'
        with open(result_filename, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.set_result(data)

    def set_result(self, data):
        self.result_json = data
        print('\n--- END STT ---\n')
        self.view_results()
        self.callback_fn(self.result_texts)

    def get_result_texts(self):
        self.result_texts.clear()
        results = self.result_json['results']
        for result in results:
            self.result_texts.append(result['alternatives'][0]['transcript'].replace(' ', ''))

    def view_results(self):
        self.get_result_texts()
        for text in self.result_texts:
            print(text)


def init():
    lambda_fn = lambda: print('done')
    ibm_stt = IBM_STT('sound_data/manner_lecture.wav', lambda_fn)
    ibm_stt.stt(target_dir='stt_results/sample/')


if __name__ == '__main__':
    init()
