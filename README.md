Parsers analysis
-----------------------

Evaluation of three parsers on 10 chosen sentences.

The selected parsers (and useful resources) are listed below :
- The StanfordNLP Parser. 
    * https://www.analyticsvidhya.com/blog/2019/02/stanfordnlp-nlp-library-python/
    * https://stanfordnlp.github.io/stanfordnlp/installation_usage.html#getting-started
- The Berkeley Neural Parser.
    * https://github.com/nikitakit/self-attentive-parser
- RASP (only available on Linux/OS)
    * http://users.sussex.ac.uk/~johnca/rasp/

For the Berkeley Neural Parser a conversion was necessary to convert trees to grammar relations. We used the Stanford conversion script.
- https://github.com/dmcc/PyStanfordDependencies

To evaluate the accuracies of the different parsers, we used gold standards using Stanford Dependencies and CoNLL-X format.

Installation
----------------------
All code was executed using Python 3 and a virtual environment.

#### Changing the configuration file
Change the OS if necessary.
Set the `config_benepar`'s keys values to False if using the Berkeley Parser for a first usage (when using the parser the right model will be automatically downloaded.) 

#### Requirements and troubleshooting 
Use `pip install -r requirements.txt` to install the requirements. You might encounter the following errors :
- Sometimes torch does not install correctly using the given syntax. In this case, install it by downloading it directly with the web using `pip install http://download.pytorch.org/whl/cpu/torch-1.1.0-cp37-cp37m-win_amd64.whl`. Then re run the requirements command.
- "Error : Object detection with Attribute error : module tensorflow has no
  attribute graphdef in tf2x" => one way to overcome this is to download tensorflow==1.14. This should be the given version on the `requirements.txt` file.

#### Installing packages directly from the command line
Some parsers require a specific separate installation. In order to initialize some of them, run `python init_parser.py` command.

#### Downloading parser models.
When first using the parsers, the parser models will need to be downloaded. Code was included within the parsers' class to download them automatically when running the main script, however you can also decide to download them in the first place. For all of them you will need to enter the Python terminal.
- For the StanfordNLP parser 
```python
import stanfordnlp
stanfordnlp.download('en')
```
You will be asked whether you want to store it in an alternate directory, press yes and enter the following directory : `'./stanfordnlp_resources'`
- For the Berkeley Neural parser 
```python
import nltk
nltk.download('punkt')
import benepar
benepar.download('benepar_en2')
```
- For RASP : download the model (it should be a folder - rasp3os) on the website and store it on the root of this repository. Follow the README instructions to have it set up. The scripts we will be using are stored in the `scripts` folder of the `rasp3os` folder. If permission is denied when trying to run one of the two shell scripts, go into the given directory and enter `chmod +x ./rasp.sh` and `chmod +x ./rasp_parse.sh`
- When using the Stanford conversion script you might encounter a `[WinError 32]` error. One way to overcome this issue (although not optimal) it to change line 87 of `venv\lib\site-packages\StanfordDependencies\SubprocessBackend.py` : instead of `os.remove(input_file.name)`, simply write `pass`
