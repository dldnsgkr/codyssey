from __future__ import annotations

import argparse
import datetime as dt
import importlib
import sys
import wave
from dataclasses import dataclass
from pathlib import Path


SAMPLE_RATE = 44_100
CHANNELS = 1
SAMPLE_WIDTH = 2
RECORDS_DIR = Path(__file__).resolve().parent / 'records'
TIMESTAMP_FORMAT = '%Y%m%d-%H%M%S'


@dataclass(frozen = True)
class MicrophoneDevice:
    index: int
    name: str
    channels: int
    backend: str


class RecorderError(Exception):
    pass


class BaseRecorderBackend:
    name = 'base'

    def list_microphones(self) -> list[MicrophoneDevice]:
        raise NotImplementedError

    def record(
        self,
        output_path: Path,
        seconds: int,
        device_index: int | None = None,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
    ) -> None:
        raise NotImplementedError


class SoundDeviceBackend(BaseRecorderBackend):
    name = 'sounddevice'

    def __init__(self) -> None:
        self.sounddevice = importlib.import_module('sounddevice')

    def list_microphones(self) -> list[MicrophoneDevice]:
        devices = []
        for index, device in enumerate(self.sounddevice.query_devices()):
            max_input_channels = int(device.get('max_input_channels', 0))
            if max_input_channels <= 0:
                continue
            devices.append(
                MicrophoneDevice(
                    index = index,
                    name = str(device.get('name', 'Unknown')),
                    channels = max_input_channels,
                    backend = self.name,
                )
            )
        return devices

    def record(
        self,
        output_path: Path,
        seconds: int,
        device_index: int | None = None,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
    ) -> None:
        target_channels = channels
        if device_index is not None:
            device_info = self.sounddevice.query_devices(device_index)
            available_channels = int(device_info.get('max_input_channels', 0))
            if available_channels <= 0:
                raise RecorderError('선택한 장치는 입력을 지원하지 않습니다.')
            target_channels = min(channels, available_channels)

        frame_count = int(seconds * sample_rate)
        recording = self.sounddevice.rec(
            frame_count,
            samplerate = sample_rate,
            channels = target_channels,
            dtype = 'int16',
            device = device_index,
        )
        self.sounddevice.wait()
        audio_bytes = recording.tobytes()
        write_wave_file(output_path, audio_bytes, sample_rate, target_channels)


class PyAudioBackend(BaseRecorderBackend):
    name = 'pyaudio'

    def __init__(self) -> None:
        self.pyaudio = importlib.import_module('pyaudio')

    def list_microphones(self) -> list[MicrophoneDevice]:
        devices = []
        interface = self.pyaudio.PyAudio()
        try:
            device_count = interface.get_device_count()
            for index in range(device_count):
                info = interface.get_device_info_by_index(index)
                max_input_channels = int(info.get('maxInputChannels', 0))
                if max_input_channels <= 0:
                    continue
                devices.append(
                    MicrophoneDevice(
                        index = index,
                        name = str(info.get('name', 'Unknown')),
                        channels = max_input_channels,
                        backend = self.name,
                    )
                )
        finally:
            interface.terminate()
        return devices

    def record(
        self,
        output_path: Path,
        seconds: int,
        device_index: int | None = None,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
    ) -> None:
        interface = self.pyaudio.PyAudio()
        frames = []
        chunk_size = 1024

        try:
            target_channels = channels
            if device_index is not None:
                info = interface.get_device_info_by_index(device_index)
                available_channels = int(info.get('maxInputChannels', 0))
                if available_channels <= 0:
                    raise RecorderError('선택한 장치는 입력을 지원하지 않습니다.')
                target_channels = min(channels, available_channels)

            stream = interface.open(
                format = self.pyaudio.paInt16,
                channels = target_channels,
                rate = sample_rate,
                input = True,
                input_device_index = device_index,
                frames_per_buffer = chunk_size,
            )

            try:
                total_chunks = int(sample_rate / chunk_size * seconds)
                for _ in range(total_chunks):
                    frames.append(stream.read(chunk_size, exception_on_overflow = False))
            finally:
                stream.stop_stream()
                stream.close()
        finally:
            interface.terminate()

        write_wave_file(output_path, b''.join(frames), sample_rate, target_channels)


def load_backend() -> BaseRecorderBackend:
    backend_classes = [SoundDeviceBackend, PyAudioBackend]
    errors = []

    for backend_class in backend_classes:
        try:
            return backend_class()
        except ModuleNotFoundError as error:
            errors.append(f'{backend_class.name}: {error}')

    error_message = [
        '사용 가능한 녹음 백엔드를 찾을 수 없습니다.',
        '다음 외부 라이브러리 중 하나를 설치해야 합니다: sounddevice, pyaudio',
    ]
    if errors:
        error_message.append('확인 결과: ' + '; '.join(errors))
    raise RecorderError('\n'.join(error_message))


def write_wave_file(
    output_path: Path,
    audio_bytes: bytes,
    sample_rate: int,
    channels: int,
) -> None:
    output_path.parent.mkdir(parents = True, exist_ok = True)
    with wave.open(str(output_path), 'wb') as wave_file:
        wave_file.setnchannels(channels)
        wave_file.setsampwidth(SAMPLE_WIDTH)
        wave_file.setframerate(sample_rate)
        wave_file.writeframes(audio_bytes)


def parse_date_input(value: str, is_end: bool = False) -> dt.datetime:
    formats = (
        ('%Y%m%d-%H%M%S', False),
        ('%Y%m%d', True),
    )

    for format_string, is_date_only in formats:
        try:
            parsed = dt.datetime.strptime(value, format_string)
            if is_end and is_date_only:
                return parsed + dt.timedelta(days = 1) - dt.timedelta(seconds = 1)
            return parsed
        except ValueError:
            continue

    raise argparse.ArgumentTypeError(
        '날짜 형식은 YYYYMMDD 또는 YYYYMMDD-HHMMSS 이어야 합니다.'
    )


def make_record_filename(now: dt.datetime | None = None) -> str:
    current_time = now or dt.datetime.now()
    return f'{current_time.strftime(TIMESTAMP_FORMAT)}.wav'


def create_output_path() -> Path:
    return RECORDS_DIR / make_record_filename()


def read_recording_timestamp(file_path: Path) -> dt.datetime | None:
    try:
        return dt.datetime.strptime(file_path.stem, TIMESTAMP_FORMAT)
    except ValueError:
        return None


def list_recording_files(
    start_date: dt.datetime | None = None,
    end_date: dt.datetime | None = None,
) -> list[Path]:
    if not RECORDS_DIR.exists():
        return []

    matched_files = []
    for file_path in sorted(RECORDS_DIR.glob('*.wav')):
        timestamp = read_recording_timestamp(file_path)
        if timestamp is None:
            continue
        if start_date is not None and timestamp < start_date:
            continue
        if end_date is not None and timestamp > end_date:
            continue
        matched_files.append(file_path)
    return matched_files


def print_microphones(devices: list[MicrophoneDevice]) -> None:
    if not devices:
        print('인식된 마이크가 없습니다.')
        return

    for device in devices:
        print(
            f'[{device.index}] {device.name} '
            f'(입력 채널: {device.channels}, 백엔드: {device.backend})'
        )


def print_recordings(files: list[Path]) -> None:
    if not files:
        print('조건에 맞는 녹음 파일이 없습니다.')
        return

    for file_path in files:
        stat_result = file_path.stat()
        print(
            f'{file_path.name} | '
            f'{dt.datetime.fromtimestamp(stat_result.st_mtime).strftime(TIMESTAMP_FORMAT)} | '
            f'{stat_result.st_size} bytes'
        )


def validate_seconds(value: str) -> int:
    try:
        seconds = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError('녹음 시간은 정수여야 합니다.') from error

    if seconds <= 0:
        raise argparse.ArgumentTypeError('녹음 시간은 1초 이상이어야 합니다.')
    return seconds


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description = '화성 생활 기록용 음성 녹음 도구입니다.'
    )
    subparsers = parser.add_subparsers(dest = 'command', required = True)

    devices_parser = subparsers.add_parser(
        'devices',
        help = '현재 인식 가능한 마이크 목록을 출력합니다.',
    )
    devices_parser.set_defaults(handler = handle_devices)

    record_parser = subparsers.add_parser(
        'record',
        help = '지정한 시간만큼 음성을 녹음합니다.',
    )
    record_parser.add_argument(
        '--seconds',
        type = validate_seconds,
        required = True,
        help = '녹음할 시간(초)',
    )
    record_parser.add_argument(
        '--device',
        type = int,
        default = None,
        help = '사용할 마이크 장치 번호',
    )
    record_parser.set_defaults(handler = handle_record)

    list_parser = subparsers.add_parser(
        'list',
        help = '저장된 녹음 파일을 조회합니다.',
    )
    list_parser.add_argument(
        '--start',
        type = parse_date_input,
        default = None,
        help = '조회 시작 날짜(YYYYMMDD 또는 YYYYMMDD-HHMMSS)',
    )
    list_parser.add_argument(
        '--end',
        type = lambda value: parse_date_input(value, is_end = True),
        default = None,
        help = '조회 종료 날짜(YYYYMMDD 또는 YYYYMMDD-HHMMSS)',
    )
    list_parser.set_defaults(handler = handle_list)

    return parser


def handle_devices(_args: argparse.Namespace) -> int:
    backend = load_backend()
    devices = backend.list_microphones()
    print_microphones(devices)
    return 0


def handle_record(args: argparse.Namespace) -> int:
    backend = load_backend()
    output_path = create_output_path()

    print(f'녹음을 시작합니다. 저장 위치: {output_path}')
    backend.record(
        output_path = output_path,
        seconds = args.seconds,
        device_index = args.device,
    )
    print(f'녹음이 완료되었습니다: {output_path.name}')
    return 0


def handle_list(args: argparse.Namespace) -> int:
    if args.start and args.end and args.start > args.end:
        raise RecorderError('시작 날짜는 종료 날짜보다 늦을 수 없습니다.')

    files = list_recording_files(start_date = args.start, end_date = args.end)
    print_recordings(files)
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return args.handler(args)
    except RecorderError as error:
        print(error, file = sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('\n녹음이 사용자에 의해 중단되었습니다.', file = sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
