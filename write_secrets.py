import os
import base64
from pathlib import Path

def write_file_from_b64_env(env_var_name: str, out_path: str, mode=0o600):
    """
    If env_var_name exists, decode it as base64 and write to out_path.
    Returns True if file written, False if env var not present.
    """
    b64 = os.getenv(env_var_name)
    if not b64:
        return False

    data = base64.b64decode(b64)
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)
    try:
        os.chmod(p, mode)
    except Exception:
        # chmod may fail on Windows; not critical
        pass
    return True
