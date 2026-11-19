"""Real stdio smoke test: python test/smoke_distribution.py COMMAND [ARGS...]."""
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading


def main():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory).resolve()
        pack = root / "external pack ü.cmake"
        pack.write_text("## function(distribution_probe EXTERNAL)\n", encoding="utf-8")
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        process = subprocess.Popen(sys.argv[1:], cwd=root, env=env,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        messages = queue.Queue()
        notifications = []

        def read():
            try:
                while True:
                    headers = {}
                    while True:
                        line = process.stdout.readline()
                        if not line:
                            raise EOFError("Server stdout closed")
                        if line == b"\r\n":
                            break
                        key, value = line.decode().split(":", 1)
                        headers[key.lower()] = value.strip()
                    messages.put(json.loads(process.stdout.read(int(headers["content-length"]))))
            except Exception as error:
                messages.put(error)

        threading.Thread(target=read, daemon=True).start()

        def send(method, params=None, identifier=None):
            payload = {"jsonrpc": "2.0", "method": method}
            if params is not None:
                payload["params"] = params
            if identifier is not None:
                payload["id"] = identifier
            data = json.dumps(payload).encode()
            process.stdin.write(f"Content-Length: {len(data)}\r\n\r\n".encode() + data)
            process.stdin.flush()

        def response(identifier):
            while True:
                item = messages.get(timeout=30)
                if isinstance(item, Exception):
                    raise item
                if item.get("id") == identifier:
                    assert "error" not in item, item
                    return item["result"]
                notifications.append(item)

        try:
            send("initialize", {"processId": None, "rootUri": root.as_uri(), "capabilities": {},
                               "initializationOptions": {"fleurdelys": {"enableCMakeAnnotations": True,
                                                        "additionalAnnotations": [str(pack)]}}}, 1)
            response(1)
            send("initialized", {})
            uri = (root / "consumer.cmake").as_uri()
            send("textDocument/didOpen", {"textDocument": {"uri": uri, "languageId": "cmake", "version": 1, "text": ""}})
            params = {"textDocument": {"uri": uri}, "position": {"line": 0, "character": 0}}
            send("textDocument/completion", params, 2)
            labels = {item["label"] for item in response(2)["items"]}
            assert {"set", "add_executable", "distribution_probe"} <= labels, labels
            send("textDocument/didChange", {"textDocument": {"uri": uri, "version": 2},
                 "contentChanges": [{"text": "distribution_probe(EXTERNAL)\nadd_executable(app main.c)\n"}]})
            feature_params = {"textDocument": {"uri": uri}, "position": {"line": 0, "character": 2}}
            send("textDocument/hover", feature_params, 5)
            assert "EXTERNAL" in response(5)["contents"]["value"]
            send("textDocument/definition", feature_params, 6)
            assert response(6)["uri"] == pack.as_uri()
            send("textDocument/definition", {"textDocument": {"uri": uri}, "position": {"line": 1, "character": 2}}, 10)
            bundled_uri = response(10)["uri"]
            assert bundled_uri.endswith("/annotations/cmake.cmake"), bundled_uri
            if Path(sys.argv[1]).name.startswith("fleurdelys"):
                assert "/fleurdelys/annotations/cmake.cmake" in bundled_uri, bundled_uri
            if "wheel-env" in sys.argv[1]:
                assert "/site-packages/fleurdelys/annotations/" in bundled_uri, bundled_uri
            feature_params["position"]["character"] = len("distribution_probe(")
            send("textDocument/signatureHelp", feature_params, 7)
            assert response(7)["signatures"][0]["label"] == "distribution_probe(EXTERNAL)"
            send("textDocument/didChange", {"textDocument": {"uri": uri, "version": 3}, "contentChanges": [{"text": "distribution_probe(WRONG)\n"}]})
            send("textDocument/hover", feature_params, 8)
            response(8)
            diagnostics = [n["params"]["diagnostics"] for n in notifications if n.get("method") == "textDocument/publishDiagnostics" and n["params"]["uri"] == uri]
            assert any("Invalid arguments" in d["message"] for d in diagnostics[-1])
            pack.write_text("## function(distribution_probe WRONG)\n", encoding="utf-8")
            send("workspace/didChangeWatchedFiles", {"changes": [{"uri": pack.as_uri(), "type": 2}]})
            send("textDocument/hover", feature_params, 9)
            response(9)
            diagnostics = [n["params"]["diagnostics"] for n in notifications if n.get("method") == "textDocument/publishDiagnostics" and n["params"]["uri"] == uri]
            assert diagnostics[-1] == [], diagnostics[-1]
            send("textDocument/didChange", {"textDocument": {"uri": uri, "version": 4}, "contentChanges": [{"text": ""}]})
            send("workspace/didChangeConfiguration", {"settings": {"fleurdelys": {"enableCMakeAnnotations": False, "additionalAnnotations": []}}})
            send("textDocument/completion", params, 3)
            labels = {item["label"] for item in response(3)["items"]}
            assert "set" in labels and "add_executable" not in labels and "distribution_probe" not in labels
            send("shutdown", identifier=4)
            response(4)
            send("exit")
            assert process.wait(timeout=10) == 0
            print("PASS: stdio initialization, bundled/core/external completion, live removal, unrelated cwd")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            errors = process.stderr.read().decode(errors="replace")
            if errors:
                print(errors, file=sys.stderr)


if __name__ == "__main__":
    main()
