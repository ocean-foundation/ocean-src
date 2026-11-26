"""Verify libcurl dependencies in cold, cached and uncached executable builds."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import time

compiler = Path(sys.argv[1]).resolve()
stdlib = Path(__file__).resolve().parents[3]
build_timeout = int(os.environ.get('OCEAN_HTTP_BUILD_TIMEOUT', '120'))
assert 1 <= build_timeout <= 3600
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
with tempfile.TemporaryDirectory(prefix='ocean-http-link-') as directory:
    root = Path(directory)
    source = root/'main.oc'
    source.write_text('''package main;
import "net/http";
func main() int {
    client: http.Client;
    result := client.Get("http://localhost:0");
    if (!result.hasError()) return 1;
    return 0;
}
''')
    binary = root/('program.exe' if os.name == 'nt' else 'program')
    env = dict(os.environ, OCEAN_SRC=str(stdlib), OCEAN_BUILD_CACHE=str(root/'cache'))
    def run(*args):
        timeout = build_timeout if Path(args[0]) == compiler else 30
        print('START linking:', *map(str, args), 'timeout=', timeout, flush=True)
        started = time.monotonic()
        try:
            p = subprocess.run([str(a) for a in args], env=env, capture_output=True, text=True,encoding="utf-8", timeout=timeout)
        except subprocess.TimeoutExpired as error:
            print('TIMED OUT linking:', args, 'stdout=', error.stdout, 'stderr=', error.stderr, flush=True)
            raise
        print('DONE linking:', args[0], 'exit=', p.returncode, 'elapsed=', round(time.monotonic()-started, 2), flush=True)
        assert p.returncode == 0, (args,p.stdout,p.stderr)
        return p.stdout

    def links_curl():
        if sys.platform == 'darwin':
            imports = run('otool', '-L', binary)
        elif os.name == 'nt':
            imports = run('llvm-objdump', '-p', binary)
        else:
            imports = run('readelf', '-d', binary)
        return 'libcurl' in imports.lower()

    for _ in range(2):
        run(compiler, 'build', source, '-o', binary)
        run(binary)
        assert links_curl()
        binary.unlink()
    run(compiler, 'check', source)
    run(compiler, 'build', stdlib/'net/http', '-o', root/'http.o')
    env['OCEAN_BUILD_CACHE']='off'
    run(compiler, 'build', source, '-o', binary)
    run(binary)
    assert links_curl()
    source.write_text('package main; func main() int { return 0; }')
    env['OCEAN_BUILD_CACHE']=str(root/'plain-cache')
    for _ in range(2):
        run(compiler, 'build', source, '-o', binary)
        run(binary)
        assert not links_curl()
        binary.unlink()
print('HTTP cold, hot and uncached linking passed. Unrelated programs do not link libcurl.')
