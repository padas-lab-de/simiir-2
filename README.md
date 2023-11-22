# SimIIR 2.0

SimIIR 2.0 extends the Python-based SimIIR framework for simulating interactive information retrieval (IIR) that was originally released by Leif Azzopardi and David Maxwell [https://github.com/leifos/simiir]. 

SimIIR 2.0 supports Python3 and includes several datasets and additional simulation algorithms for querying and other user interactions.

## Framework Architecture

![The architecture of our extended SimIIR framework, with the components split across both simulation and user categories. Simulation components define the simulation — a representation of some real‐world user study, with user components defining the behavior of simulated users.](https://github.com/padre-lab-eu/extended-simiir/blob/main/simiir2.png)

## Installation

Add the ifind and SimIIR library to your PYTHONPATH.

To evaluate the effectiveness of the simulated sessions, you will need to download trec_eval [http://trec.nist.gov/trec_eval/].

Add trec_eval to your PATH.

    #### ifind and SimIIR
    export PYTHONPATH="${PYTHONPATH}:/pathTo/ifind:/pathTo/simiir"

    #### trec_user
    export PATH="/pathTo/trec_eval-9.0.7:$PATH"

Create a virtual environment with the packages in requirements.txt (this is the same as the one for ifind).

## Dataset

In our experiments, we use the Sowiport User Search Session dataset (SUSS) dataset.
The dataset is publicly available at [https://doi.org/10.7802/1380].

SimIIR simulate user search session using only a list of five major actions: QUERY (i.e., formulating a query), SERP (i.e., viewing the search result page), SNIPPET (i.e., viewing the document’s metadata), DOC (i.e., viewing the full document’s content) and MARK (i.e., marking the document as relevant or not). We therefore cluster SUSS’s list of actions and pages into broader groups to match the actions we have available in SimIIR (e.g., "QUERY"
action in SimIIR represents the group of actions "issue a first query", "reformulate a query" and "click query suggestion" in SUSS) and remove the non-search related actions (e.g., visiting the home page).

However, any other user behavior dataset can be used to analyze search session logs and extract user-types models following the same method.

## Example of experiments

Create a directory called output in example_sims

cd into the simiir directory, and run:

    python run_simiir.py ../example_sims/trec_bm25_simulation.xml

or

    python run_simiir.py ../example_sims/trec_pl2_simulation.xml

You will see the simulations running where the simulated users use either BM25 or PL2.

The output of the simulations will be in example_sims/output.


## Configuration via simulation.xml files

A simulation requires four main elements: output, topics, users, and a search interface.

### output
This is where the output of the simulation is to be stored.
If you do not want to use trec_eval, set trec_eval to false and it will not automatically evaluate the output of the simulations.


### topics
A set of sample topics have been included in example_data/topics.
You can include each topic that you would like the simulated users to undertake.


### users

A user configuration file contains several parameters that describe user search behavior:
* **queryGenerator** allows to define which strategy the user is adapting to generate his/her queries. 
* **textClassifiers** denotes the method used to assess a document/snippet for relevance. 
* **stoppingDecisionMaker** defines the stopping decision point at which the user stops interacting with the SERP. 
* **logger** denotes the amount of time required for the user to interact with the system. 
* **searchContext** keeps track of all the user's interaction with the system. 
* **serpImpression** is responsible for determining whether the presented SERP is relevant enough to enter and examine in more detail.

A set of sample users have been created and included in example_sims/users.

You can include however many users you would like to use the searchInterface for the specified topics.

Each of the users have been configured differently to show how the different components can be set to instantiate different simulated users.

    #### trec_user
    Submits one query, the topic title.

    Examines each snippet and each document, and considers them relevant.

    #### fixed_depth_user

    Submits three word queries -- generated from the topic description

    Examines to a fixed depth, initially set to 10.

    For each snippet that the fixed_depth_user examines, it stochastically decides whether it should examine the document or not based on the specified probabilities.

    For each document that the fixed_depth_user examines, it stochastically decides whether it should mark it as relevant or not based on the specified probabilities.


### search interface
The search interface is a programmatic representation of the search interface an actual user would use.

It currently lets the simulated user do two actions: query and examine a document.

Note: the simulator acts as a broker to query and fetch documents, and controls the flow of actions (i.e., querying, examining snippets, assessing documents, marking documents as relevant).

So far, one search interface is specified which connects to a Whoosh-based index of TREC documents.












