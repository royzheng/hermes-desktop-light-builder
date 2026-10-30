#!/usr/bin/env python3
"""Exercise the installer against isolated macOS app fixtures, never /Applications."""
import os
import plistlib
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    script = Path(__file__).with_name('Install.command')
    subprocess.run(['bash', '-n', str(script)], check=True)
    with tempfile.TemporaryDirectory(prefix='hermes-installer-test-') as temp:
        root = Path(temp)
        disk = root / 'Mounted disk with spaces'
        dest = root / 'Applications'
        disk.mkdir()
        dest.mkdir()
        shutil.copy2(script, disk / script.name)
        source = disk / 'Hermes Light.app'
        contents = source / 'Contents'
        contents.mkdir(parents=True)
        plist = contents / 'Info.plist'
        identity = {'CFBundleIdentifier': 'com.nousresearch.hermes-light',
                    'CFBundleExecutable': 'HermesInstallerFixture', 'CFBundleShortVersionString': '1.0'}
        plist.write_bytes(plistlib.dumps(identity))
        (contents / 'payload').write_text('first version')
        command = [str(disk / script.name), '--destination', str(dest), '--no-open', '--no-pause']

        def run(ok=True):
            result = subprocess.run(command, text=True, capture_output=True)
            assert (result.returncode == 0) == ok, result.stdout + result.stderr

        subprocess.run(['xattr', '-w', 'com.apple.quarantine', '0083;00000000;InstallerTest;', str(source)], check=True)
        run()
        target = dest / source.name
        assert (target / 'Contents/payload').read_text() == 'first version'
        assert 'com.apple.quarantine' not in subprocess.check_output(['xattr', str(target)], text=True)
        (contents / 'payload').write_text('second version')
        run()
        assert (target / 'Contents/payload').read_text() == 'second version'
        assert not list(dest.glob('.hermes-light-install.*'))
        identity['CFBundleIdentifier'] = 'invalid.app'
        plist.write_bytes(plistlib.dumps(identity))
        run(ok=False)
        assert (target / 'Contents/payload').read_text() == 'second version'
        identity['CFBundleIdentifier'] = 'com.nousresearch.hermes-light'
        plist.write_bytes(plistlib.dumps(identity))
        saved = dest / 'Saved.app'
        target.rename(saved)
        target.symlink_to(saved, target_is_directory=True)
        run(ok=False)
        assert target.is_symlink() and (saved / 'Contents/payload').read_text() == 'second version'
        target.unlink()
        saved.rename(target)
        fake_process = root / 'HermesInstallerFixture'
        shutil.copy('/bin/sleep', fake_process)
        process = subprocess.Popen([str(fake_process), '30'])
        try:
            # Wait until the actual fixture executable has replaced the child process.
            import time
            for _ in range(100):
                if subprocess.run(['pgrep', '-x', fake_process.name], capture_output=True).returncode == 0:
                    break
                time.sleep(.02)
            else:
                raise AssertionError('fixture process did not start')
            run(ok=False)
        finally:
            process.terminate()
            process.wait()
        assert (target / 'Contents/payload').read_text() == 'second version'
    print('PASS: first install, replacement, quarantine removal, wrong identity, symlink and running-app refusal')


if __name__ == '__main__':
    main()
