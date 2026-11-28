# Cybersecurity Exercise Analysis and Recommendation

**Authors:** Nora Liis Palm, Liisi Parve, Maileen Rohtmets  
**Course:** Introduction to Data Science, University of Tartu, autumn 2026

## Motivation and goals

RiskSight is a company that develops cybersecurity exercises for business leaders. 
Selecting a suitable exercise requires understanding the threats it covers, the
decisions participants must make, and the possible consequences for the organization.

Developing a complete solution would require more time than available for this course project, 
as discussed with RiskSight. Our project is a prototype that organizes information from 
CISA cybersecurity exercise manuals and connects it with data from MITRE ATT&CK.

The project's goals are:

1. Identify and analyse cybersecurity threats, possible responses, and
   business consequences.
2. Develop a structured data model connecting scenarios, response
   options, and potential outcomes.
3. Develop and evaluate an exercise recommendation model based on
   threat type, difficulty, and required skills.

## Data

We use two sources:

- **CISA tabletop exercise manuals:** 8 manuals covering healthcare,
  vendor supply-chain compromise, ransomware, insider threats,
  executive leadership, industrial control systems, financial services,
  and communications.
- **MITRE ATT&CK:** Enterprise and Industrial Control Systems datasets
  describing attack techniques, mitigations, and their relationships.

The prepared CISA data contains 66 scenario events and 425 discussion 
questions, grouped into 16 exercises.

The MITRE tables contain 810 techniques, 97 mitigations, and 1,901
technique–mitigation relationships.

The CISA scenarios are fictional training material. Their frequencies
describe our selected exercise catalogue, not the frequency of real-world
cybersecurity incidents.

## Repository structure

| Location | Contents                                                                                  |
|---|-------------------------------------------------------------------------------------------|
| `data/raw/` | Source CISA documents and MITRE ATT&CK JSON files                                         |
| `data/processed/` | CSV files containing scenario events, questions, labels, MITRE connections, and exercise summaries |
| `notebooks/` | Python notebooks used for data preparation, analysis, and recommendation                  |
| `figures/` | Exported figures for presenting the results                                               |
| `app.py` | Prototype app for viewing scenarios and recording answers                                 |
| `requirements.txt` | Python packages needed to run the app                                    |

## Notebooks

Run the numbered notebooks in the following order:

| Notebook | Purpose                                                                   |
|---|---------------------------------------------------------------------------|
| `1_cisaFileReading_done.ipynb` | Extracts scenario events and discussion questions from CISA manuals       |
| `2_mitreFileReading_DONE.ipynb` | Extracts MITRE techniques, mitigations, and relationships                 |
| `3_GivingEventsThreatLevel-CISA.ipynb` | Assigns threat and business-impact labels to scenario events              |
| `4_GroupingCisaDataIntoExercises.ipynb` | Combines events and questions into 16 exercises                           |
| `5_CisaMitreCombining.ipynb` | Connects events to MITRE attack techniques and possible responses         |
| `6_label_questions.ipynb` | Labels questions by required skill and difficulty using keywords        |
| `7_recommend_exercises.ipynb` | Recommends exercises and checks the quality of the recommendations |

## Methods

### Goal 1: Descriptive analysis

We manually label the threats and business impacts in each scenario, compare 
how often they appear, and use keywords to identify the responses discussed in
the questions.

### Goal 2: Structured data model

We connect exercises to events, events to possible MITRE attack techniques, 
and techniques to measures that could help prevent or reduce their effects. 
Each event also has a business impact.

We choose the technique connections manually and provide a written explanation 
for each choice. We also use TF-IDF text similarity as a simple method for comparison.

### Goal 3: Exercise recommendation

Each exercise has a profile describing its threats and the skills
and difficulty levels of its discussion questions.

The recommender scores each exercise based on the proportion of its events 
and questions that match the requested threat, skill, and difficulty. 
It uses fixed rules to recommend exercises based on their content.

We compare the recommendations by choosing exercises randomly, placing 
exercises with more questions first, and matching only by threat type.
We measure how often a suitable exercise appears in the top three results 
(Hit@3) and how high suitable exercises appear in the rankings 
(mean reciprocal rank, or MRR).

## Reproducing the analysis

### 1. Obtain the repository

Clone or download this repository and open a terminal in its root folder.

### 2. Install Python packages

Use a Python environment with Jupyter Notebook and the following packages:

    python -m pip install jupyter pandas numpy matplotlib scikit-learn python-docx requests reportlab streamlit

The current `requirements.txt` lists only the app dependencies, so it is
not sufficient on its own to reproduce all notebooks.

### 3. Run the notebooks

Start Jupyter from the repository root:

    jupyter notebook

Open the notebooks in `notebooks/` and run them in the order listed above.
Use **Kernel → Restart & Run All** in each notebook to clear previous variables 
and run all cells from the beginning.

Generated CSV tables are saved in `data/processed/`. The additional Goal 1
notebook saves its presentation figures in `figures/`.

### 4. Run the demonstration app

After generating the prepared data, run:

    streamlit run app.py

The app lets users select a scenario package, navigate its events, record
discussion answers, and download an after-action report. The recommender
is currently demonstrated in notebook 07 and is not integrated into the app.

## Main outputs

| File | Contents |
|---|---|
| `cisa_classified_events.csv` | Scenario events with threat and impact labels |
| `cisa_exercises.csv` | Exercise catalogue with event and question links |
| `cisa_event_techniques.csv` | Event–technique relationships |
| `cisa_event_mitigations.csv` | Event–technique–mitigation relationships |
| `scenario_model.csv` | Combined event-level scenario model |
| `goal2_exercise_model.csv` | Exercise-level summary of techniques, responses, and impacts |
| `cisa_questions_labeled.csv` | Discussion questions with skill and difficulty labels |
| `goal3_exercise_dataset.csv` | Readable exercise-level summary for recommendation |
| `recommender_evaluation.csv` | Recommendation results compared with baselines |

All tables above are stored in `data/processed/`.

## Current limitations

- The catalogue contains only 16 exercises from eight selected manuals.
- Threat labels and MITRE mappings involve interpretation and require
  manual review.
- Question skill and difficulty labels come from keyword rules. The
  prepared manual-check sheet has not yet been completed.
- Question difficulty is a proxy for the thinking required, not a measure
  of actual participant performance.
- Recommendation evaluation uses requests generated from the existing
  questions. Repeated questions and shared source material limit its
  independence.
- The project does not yet establish whether real trainers find the
  recommendations useful.

## Sources

- CISA cybersecurity scenarios:
  https://www.cisa.gov/resources-tools/resources/cybersecurity-scenarios
- MITRE ATT&CK:
  https://attack.mitre.org/
- MITRE ATT&CK STIX datasets:
  https://github.com/mitre-attack/attack-stix-data