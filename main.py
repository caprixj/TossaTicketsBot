import logging
import sys

import uvicorn

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    uvicorn.run("webhook_app:create_app", factory=True, host="0.0.0.0", port=8000)
