# Generating the dataset PS-ProofWiki

Welcome :smile:

This is the code used for generating the PS-ProofWiki. A dataset for Premise Selection in mathematical texts.

Paper: Deborah Ferreira, André Freitas, Natural Language Premise Selection: Finding Supporting Statements for Mathematical Texts, 12th Language Resources and Evaluation Conference (LREC), Marseille, France, 2020 (Language Resource Paper). [<pdf>](https://arxiv.org/abs/2004.14959)

## Dataset

The dataset can be found in the folder dataset.

## Requirements

Run this command to download the data dump:

```
wget https://proofwiki.org/xmldump/latest.xml -O data/wiki.xml
```

Note: this might give you a slightly modified (updated) version of the dataset.

Run this command to install the requirements:

```
pip install -r requirements.txt

export PREFECT__FLOWS__CHECKPOINTING=true

```

## Running the extraction

After you installed all the requirements, run the extraction with

```
 python -m nlps_extraction.flows.extract_proofwiki
```

This will generate the files:

```
/output/train.json
/output/test.json
/output/dev.json
/output/kb.json
```

## Running Baselines

TF-IDF

```
python -m nlps_extraction.flows.baselines.run_tfidf_experiment
```

Doc2Vec

S-Bert

## Citation

If you use our dataset or this pipeline to generate a new version of the dataset or use our dataset, please cite us:

```
@article{ferreira_freitas_lrec_2020,
 title={Natural Language Premise Selection: Finding Supporting Statements for Mathematical Texts.},
 journal={12th Language Resources and Evaluation Conference (LREC), Marseille, France.},
 author={Ferreira, Deborah and Freitas, Andre},
 year={2020},
 month={May}}
```

## Contact us

If you have any question, suggestions or ideas related to this dataset, please do not hesitate to contact me.

deborah[dot]ferreira[at]manchester[dot]ac[dot]uk
