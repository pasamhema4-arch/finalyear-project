import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(HERE, "mindscan-ai-flask")
INNER_APP_PATH = os.path.join(PROJECT_DIR, "app.py")

sys.path.insert(0, PROJECT_DIR)

spec = importlib.util.spec_from_file_location("mindscan_app", INNER_APP_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

app = module.app

if __name__ == "__main__":
    app.run(debug=True)
