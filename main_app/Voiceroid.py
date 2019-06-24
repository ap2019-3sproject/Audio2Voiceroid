import subprocess


class Voiceroid:
    def __init__(self, id, seika_path):
        self.id = id
        self.seika_path = seika_path

    def talk(self, params):
        command = [self.seika_path, '-cid', str(self.id)]
        for key, val in params.items():
            command.append('-' + key)
            command.append(val)

        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def test():
    voiceroid = Voiceroid(300, 'seikasay.exe')
    params = {
        'volume': '1.3',
        'speed': '1.0',
        'pitch': '0.8',
        'intonation': '0.8',
        'save': '絶対パス',
        't': '喋るテキスト'
    }
    voiceroid.talk(params)


if __name__ == '__main__':
    test()
