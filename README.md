# Welcome to error-assistant!

### Bare in mind, this is only a beta, so the functionalities might be buggy.

### Nonetheless, I believe in the power of this app, so let's make it better, TOGETHER!

---

## **Functionalities**

This assistant is being created to make the life of a developer a little bit easier (at least we try).

The main goal of the app is to make it very easy for developers to run inference on models with their error and the code base.

Everything is already given to the model; the only thing to do is to set up a custom logger that will forward an error message to the error-assistant and generate a response in the terminal!

But I am getting ahead of myself. Let's see how to get it up and running.

## **Step by Step**

1.  **Install the repo**
    a.  Clone the repo:
        ```
        git clone [https://github.com/marcoslashpro/error-assistant.git](https://github.com/marcoslashpro/error-assistant.git)
        ```

    b.  Install the repo via pip:
        ```
        pip install error-assistant
        ```

2.  **Setup the error-assistant**
    a.  The first thing to do after installation is to run `error-assistant-ce` in the terminal, which will kindly open a `config.toml` file.

    b.  Inside of the `config.toml` file, you'll find everything that you might want to set up in order to get the app up and running!

        On a high level, focus only on:
        * Inserting your `hf_token` and the `pinecone api_key`.
        * Configuring the paths that are needed.

        In there, you might also find some metadata, such as the name of the vector store index. Feel free to change them if you like.

    **NOTE:** If a **pinecone api_key** is not provided, the app will not run! ... c'mon, it's free, and also Hugging Face, they're free!

NICE! We are up and running now... Let's get this to work.

## **Commands**

**error-assistant:**
This will start the app in your terminal and will create/update the vector store with all of the new files that have been detected. Leave it running! The update of the vector store happens automatically, but for it to work, the app needs to be running.

After having called `error-assistant` from the terminal, once you are in the app:

Call `chat` or `-c`. This will prompt you to insert a message that will be passed to the model. Type `quit` or `q` to exit.

One more interesting feature is the logger:

You can, at any time from inside the directory where you have installed error-assistant, run this import statement in a Python module:

```
from error_assistant.error_assistant_config.log_config import log_config
import logging

logger = logging.getLogger(__name__)
log_config(logger)
```
After this, whenever you want to pass a specific error to the error-agent, just do:

```
try:
    'some risky expression'
except Exception as e: #substitute the ‘Exception’ with the error
    logger.agent(e)
This is going to run inference on the model with the given error!
```

P.S.
Please always have a .gitignore file, or a lot of useless files will be uploaded to the vector store. A minimal one would be:

```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*.egg-info/
*.egg

# Virtual environments
env/
.venv/

# Build
build/
dist/
*.whl

# Logs
*.log

# VS Code
.vscode/

# OS files
.DS_Store

# Test folder
src/error_assistant/tests

# Temp nano files
.swp
```
