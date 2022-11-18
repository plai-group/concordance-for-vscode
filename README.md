# concordance-for-vscode
This is a little writing tool I made while procrastinating starting my thesis, based on [_Concordance_](http://www.daviddeutsch.org.uk/concordance/) from David Deutsch. It is a python script which highlights duplicate words and phrases in order to find and eliminate repetitions.  

![](concordance-demo.gif)

I've cobbled it together using python and four extensions:

1. [Dendron](https://www.dendron.so/)
2. [Regex highlight](https://marketplace.visualstudio.com/items?itemName=fabiospampinato.vscode-highlight)
3. [Command runner](https://marketplace.visualstudio.com/items?itemName=edonet.vscode-command-runner)
4. [Run on save](https://marketplace.visualstudio.com/items?itemName=emeraldwalk.RunOnSave)

In a perfect world I would have written this in javascript and it would be a simple vscode extension (accepting pull requests!). I don't know how to do that however, and so instead I've used python to write custom regex, which are then fed to [regex highlight](https://marketplace.visualstudio.com/items?itemName=fabiospampinato.vscode-highlight). [Run on save](https://marketplace.visualstudio.com/items?itemName=emeraldwalk.RunOnSave) is used to update the highlights upon save, and [command runner](https://marketplace.visualstudio.com/items?itemName=edonet.vscode-command-runner) saves an `.args` token which changes the settings. [Dendron](https://www.dendron.so/) provides the environment where the markdown notes live.

## Setup instructions 

- install python packages 
```
pip install pyjson5 seaborn nltk markdown beautifulsoup4 pandas
```
- install vscode extensions 
  1. [Dendron](https://www.dendron.so/)
  2. [Regex highlight](https://marketplace.visualstudio.com/items?itemName=fabiospampinato.vscode-highlight) 
  3. [Command runner](https://marketplace.visualstudio.com/items?itemName=edonet.vscode-command-runner)
  4. [Run on save](https://marketplace.visualstudio.com/items?itemName=emeraldwalk.RunOnSave) 
- git clone this repository and move concordance.py to `$dendron_directory/scripts/concordance.py`. 
  - the `script` subdirectory should be parallel to your `dendron.code-workspace` file.
- change line 11 - 13 of concordance.py to the appropriate paths: 

```python
SETTINGS_PATH = '/Users/vmasrani/dev/phd/dendron/dendron.code-workspace'
ARGS_PATH = '/Users/vmasrani/dev/phd/dendron/scripts/.args'
OUT_PATH = '/Users/vmasrani/dev/phd/dendron/vault/assets/concordance.csv'
```

## Modify your workspace settings to configure command-runner and runonsave

Add the following entries to your workspace settings json (command pallet > Preferences: Open Workspace Settings (JSON)), with the paths in `emeraldwalk.runonsave.commands.cmd` appropriately changed to point to your python interpreter and concordance.py file:

```json
"command-runner.commands": {
    "reset": "echo '0 0 0 1' >! ${config:dendron.rootDir}/scripts/.args && ${config:python.pythonPath} ${config:dendron.rootDir}/scripts/concordance.py '${file}'",
    "words": "echo '1 5 1 0' >! ${config:dendron.rootDir}/scripts/.args && ${config:python.pythonPath} ${config:dendron.rootDir}/scripts/concordance.py '${file}'",
    "phrases": "echo '2 6 0 0' >! ${config:dendron.rootDir}/scripts/.args && ${config:python.pythonPath} ${config:dendron.rootDir}/scripts/concordance.py '${file}'",
    "words_and_phrases": "echo '1 6 0 0' >! ${config:dendron.rootDir}/scripts/.args && ${config:python.pythonPath} ${config:dendron.rootDir}/scripts/concordance.py '${file}'",
    "long": "echo '4 10 0 0' >! ${config:dendron.rootDir}/scripts/.args && ${config:python.pythonPath} ${config:dendron.rootDir}/scripts/concordance.py '${file}'"
},
"emeraldwalk.runonsave": {
    "commands": [
        {
            "match": "\\.md$",
            "isAsync": true,
            "cmd": "/Users/vmasrani/miniconda3/envs/ml3/bin/python /Users/vmasrani/dev/phd/dendron/scripts/concordance.py ${file}",
            "autoClearConsole": true
        }
    ]
},
```

## How to use 

Select `run command` from your command pallet - this should display five options:
1. words and phrases: highlight duplicate words and phrases 
2. reset: turn off highlighting 
3. phrases: highlight duplicate phrases only 
4. long: highlight long (greater than 10 characters) phrases only 
5. words: highlight duplicate words only 

Select one of the options, then the script should automatically run every time you save a markdown file. Looking at the `Run on Save` output panel should reveal a printout of each duplicate.  


