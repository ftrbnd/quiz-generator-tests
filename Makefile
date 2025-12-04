# Detect operating system
ifeq ($(OS),Windows_NT)
    VENV_ACTIVATE := .\gradio-env\Scripts\activate
    PYTHON := python
else
    VENV_ACTIVATE := source gradio-env/bin/activate
    PYTHON := python3.12
endif
PIP_INSTALL := pip install --upgrade pip && pip install -r requirements.txt && python3.12 -m spacy download en_core_web_sm

# Install dependencies
ifeq ($(OS),Windows_NT)
install:
	$(PYTHON) -m venv gradio-env
	@echo Installing dependencies...
	@$(VENV_ACTIVATE) && ${PIP_INSTALL}
else
install:
	$(PYTHON) -m venv gradio-env
	@echo Installing dependencies...
	@bash -c "$(VENV_ACTIVATE) && ${PIP_INSTALL}"
endif

# Activate virtual environment
ifeq ($(OS),Windows_NT)
activate:
	@echo Run 'gradio src/app.py' to start the application
	@cmd /K "${VENV_ACTIVATE}"
else
activate:
	@echo Run 'gradio src/app.py' to start the application
	@cd . && bash -c "${VENV_ACTIVATE} && exec bash"
endif
