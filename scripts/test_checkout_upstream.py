#!/usr/bin/env python3
"""Exercise the workflow checkout against an isolated, advancing Git upstream."""

import os
from pathlib import Path
import subprocess
import tempfile
import textwrap


def main():
    workflow = Path(__file__).resolve().parents[1] / '.github/workflows/build-light.yml'
    step = workflow.read_text().split(
        '      - name: Check out pinned upstream main commit\n', 1
    )[1].split('\n      - name:', 1)[0]
    command = textwrap.dedent(step.split('        run: |\n', 1)[1])

    with tempfile.TemporaryDirectory(prefix='hermes-checkout-test-') as temp:
        root = Path(temp)
        source = root / 'source with spaces'
        source.mkdir()
        env = {
            **os.environ,
            'GIT_CONFIG_GLOBAL': str(root / 'gitconfig'),
            'GIT_CONFIG_NOSYSTEM': '1',
            'GIT_TERMINAL_PROMPT': '0',
        }

        def git(directory, *args):
            return subprocess.check_output(
                ['git', *args], cwd=directory, env=env, text=True,
                stderr=subprocess.PIPE,
            ).strip()

        git(source, 'init', '--initial-branch=main')
        git(source, 'config', 'user.name', 'Checkout Test')
        git(source, 'config', 'user.email', 'checkout-test@example.invalid')
        git(source, 'config', 'commit.gpgsign', 'false')
        git(source, 'config', 'uploadpack.allowFilter', 'true')
        # Redirect the real workflow URL without modifying its shell commands.
        git(source, 'config', '--global', f'url.{source.as_uri()}.insteadOf',
            'https://github.com/NousResearch/hermes-agent.git')

        config = source / 'apps/desktop/electron-builder.config.cjs'
        config.parent.mkdir(parents=True)
        config.write_text('module.exports = {};\n')
        git(source, 'add', '.')
        git(source, 'commit', '-m', 'Selected upstream commit')
        selected = git(source, 'rev-parse', 'HEAD')

        (source / 'advanced.txt').write_text('main advanced after selection\n')
        git(source, 'add', '.')
        git(source, 'commit', '-m', 'Advance main before checkout')
        advanced = git(source, 'rev-parse', 'HEAD')
        assert advanced != selected

        def checkout(name, sha):
            work = root / name
            work.mkdir()
            result = subprocess.run(
                ['bash', '-e', '-o', 'pipefail', '-c', command], cwd=work,
                env={**env, 'UPSTREAM_SHA': sha}, text=True, capture_output=True,
            )
            return work / 'upstream', result

        checkout_dir, result = checkout('main-advanced', selected)
        assert result.returncode == 0, result.stdout + result.stderr
        assert git(checkout_dir, 'rev-parse', 'HEAD') == selected
        assert not (checkout_dir / 'advanced.txt').exists()
        assert (checkout_dir / config.relative_to(source)).is_file()

        checkout_dir, result = checkout('missing-commit', '0' * 40)
        assert result.returncode != 0, 'Unavailable commit must fail checkout'
        head = subprocess.run(
            ['git', 'rev-parse', '--verify', 'HEAD'], cwd=checkout_dir,
            env=env, text=True, capture_output=True,
        )
        assert head.returncode != 0, 'Must not fall back to the current main'

        git(source, 'rm', str(config.relative_to(source)))
        git(source, 'commit', '-m', 'Remove Light packaging config')
        missing_config = git(source, 'rev-parse', 'HEAD')
        checkout_dir, result = checkout('missing-config', missing_config)
        assert git(checkout_dir, 'rev-parse', 'HEAD') == missing_config
        assert result.returncode != 0
        assert 'Selected upstream commit has no Light packaging config.' in result.stderr

    print('PASS: pinned checkout after main advances, unavailable commit rejection, and packaging-config check')


if __name__ == '__main__':
    main()
