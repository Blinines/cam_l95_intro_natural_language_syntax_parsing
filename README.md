Evaluation and comparison of parsers
-----------------------

Evaluation of three parsers on 10 chosen sentences.

The selected parsers (and useful resources) are listed below :
- The StanfordNLP Parser. 
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
All code was executed using Python 3.7.4 and a virtual environment.

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

Usage
----------------------

The two main scripts to run are `main_dep.py` and `main_evaluate.py`

* Running `main_dep.py` will parse given sentences for a specific parser, and will both save the parsed sentences in original format and in ConLL-X format. Several arguments to run the script : 
    * `-p` : which parser to use. Choose between `stanford`, `benepar` and `rasp`
    * `-l` : path to the sentences you want to parse
    * `-saveall` : path to save the parsed sentences in original format
    * `-saveconll` : path to save the parsed sentences in ConLL-X format.

Please note that when running this script all the three parsers are loaded and initialized and hence it might take some time when launching the script.

Also the RASP case is a bit particular because we used a different algorithm to get ConLL-X format, and we wanted it to work even on Windows. Hence the script first get the RASP output in its original format and save it. Then from this new file it creates the ConLL-X file.

We ran the following for our experiment (supposing in root of project) :
```python
python ./main_dep.py -p stanford -l ./data/raw/sentences.txt -saveall ./data/parsed/parsed_sentences_stanfordnlp.txt -saveconll ./data/parsed/parsed_sent_conll_stanfordnlp.txt
python ./main_dep.py -p benepar -l ./data/raw/sentences.txt -saveall ./data/parsed/parsed_sentences_benepar.txt -saveconll ./data/parsed/parsed_sent_conll_benepar.txt
python ./main_dep.py -p rasp -l ./data/raw/sentences.txt -saveall ./data/parsed/parsed_sentences_rasp.txt -saveconll ./data/parsed/parsed_sent_conll_rasp.txt
```


* Runnning `main_evaluate.py` will display quantitative metrics for a specific parser, from the corresponding table in `./analysis.xlsx`. You have to specify `-p` as argument and add which parser to choose. Like before, options are between `stanford`, `benepar` and `rasp`.
We ran the following for our experiment (supposing in root of project) :
```python
python ./main_evaluate.py -p stanford 
python ./main_evaluate.py -p benepar 
python ./main_evaluate.py -p rasp 
```


Project structure
----------------------
* [data](./data) : all sentences and parsed sentences used for experiments. 
    * [gold_standard](./data/gold_standard.txt) : our gold standard for comparison
    * [parsed](./data/parsed) : contains different type of parsed sentences
        * `parsed_modif_{num_sent}_conll_{pars_name}` : for num_sent sentence, we sometimes had to rerun pars_name on slightly modified sentences. The new parsing in ConLL-X format is stored in those files.
        * `parsed_modif_{num_sent}_{pars_name}` : same than above but only with raw output of pars_name.
        * `parsed_sent_conll_{pars_name}` : 10 original sentences parsed with pars_name, in ConLL-X format.
        * `parsed_sentences_{pars_name}`: 10 original sentences parsed with pars_name, in their original format.
    * [raw](./data/raw) : original sentences taken as input to the parsers. Modified sentences also stored there.

* [analysis](./analysis.xlsx) : Containing sentences compared and count of rightly/wrongly assigned dependencies. {pars_name} sheet contains the table, and {pars_name}-sent sheet the comparison.
* [config](./config.yaml) 
* [convert_to_latex](./convert_to_latex.py) : helper for the report. Generates automatically the Latex table with all information, as displayed in the report.
* [helpers](./helpers.py)
* [init_parser](./init_parser.py) 
* [main_dep](./main_dep) : main script to run to get parsing of sentences.
* [main_evaluate](./main_evaluate.py) : main script to run to get quantitative metrics.
* [parsers](./parser.py) : Parser classes.
* [requirements](./requirements.txt)