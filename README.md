# ts-project-initializer

A simple script to initialize typescript projects.

## How to use

1. Install requirements

```bash
pip3 install -r requirements.txt
```

2. Setup your project `template.yaml`, available keys are from this list:

- DevDependencies
- Dependencies
- ProjectDirs
- GitIgnore
- TsConfig
- Eslint
- EslintIgnore

3. Run the script:

```bash
python ts-project-init.py template.yaml [--dst-dir <directory>]
```
