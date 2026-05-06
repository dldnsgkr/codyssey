import itertools
import os
import time
import zipfile
from datetime import datetime
from multiprocessing import Pool, Value, cpu_count


CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789'
PASSWORD_LEN = 6
TOTAL = len(CHARS) ** PASSWORD_LEN
BATCH_SIZE = 10000
PREFIX_LEN = 2

_found = None
_counter = None


def _init_worker(found, counter):
    global _found, _counter
    _found = found
    _counter = counter


def _try_prefix(args):
    prefix, zip_path = args

    if _found.value:
        return None

    try:
        with zipfile.ZipFile(zip_path) as zf:
            name = zf.namelist()[0]
            local_count = 0
            remaining = PASSWORD_LEN - PREFIX_LEN

            for suffix in itertools.product(CHARS, repeat=remaining):
                if _found.value:
                    return None

                password = prefix + ''.join(suffix)
                local_count += 1

                if local_count % BATCH_SIZE == 0:
                    with _counter.get_lock():
                        _counter.value += BATCH_SIZE

                try:
                    zf.read(name, pwd=password.encode())
                    _found.value = True
                    with _counter.get_lock():
                        _counter.value += local_count % BATCH_SIZE
                    return password
                except Exception:
                    pass

            with _counter.get_lock():
                _counter.value += local_count % BATCH_SIZE

    except Exception:
        return None

    return None


def unlock_zip(zip_path):
    start_time = time.time()
    print(f'[START] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'[INFO] 전체 경우의 수: {TOTAL:,}')

    cores = cpu_count()
    print(f'[INFO] CPU 코어 수: {cores}')

    found = Value('b', 0)
    counter = Value('i', 0)

    prefixes = [
        ''.join(p)
        for p in itertools.product(CHARS, repeat=PREFIX_LEN)
    ]

    pool = Pool(
        processes=cores,
        initializer=_init_worker,
        initargs=(found, counter)
    )

    password = None
    terminated = False
    last_log_time = time.time()

    try:
        results = pool.imap_unordered(
            _try_prefix,
            [(p, zip_path) for p in prefixes]
        )

        for result in results:
            now = time.time()
            if now - last_log_time >= 2:
                elapsed = now - start_time
                tried = counter.value
                progress = tried / TOTAL * 100
                print(
                    f'[PROGRESS] 시도: {tried:,} / {TOTAL:,}'
                    f' ({progress:.4f}%) | 경과: {elapsed:.2f}초'
                )
                last_log_time = now

            if result:
                password = result
                elapsed = time.time() - start_time
                print(f'[SUCCESS] 비밀번호: {password}')
                print(f'[TIME] 총 경과 시간: {elapsed:.2f}초')
                pool.terminate()
                terminated = True
                break

        if not terminated:
            pool.close()

    except Exception as e:
        print(f'[ERROR] 처리 중 오류 발생: {e}')
        pool.terminate()

    finally:
        pool.join()

    if password is None:
        print('[FAIL] 비밀번호를 찾지 못했습니다')
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'password.txt')
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(password)
        print(f'[SAVED] {output_path}')
    except OSError as e:
        print(f'[ERROR] 파일 저장 실패: {e}')


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(base_dir, 'emergency_storage_key.zip')

    if not os.path.exists(zip_path):
        print(f'[ERROR] ZIP 파일을 찾을 수 없습니다: {zip_path}')
    else:
        unlock_zip(zip_path)
