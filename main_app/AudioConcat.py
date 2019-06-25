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
    command.append('out.wav')
    print(command)
    proc = subprocess.run(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, cwd=target_dir)
    print(proc.stdout)


def init():
    silences = [1] * 2
    concat('sound_data/temp/', 'wav', 2, silences)


if __name__ == '__main__':
    init()
