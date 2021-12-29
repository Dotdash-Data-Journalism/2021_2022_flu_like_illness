# Flu-Like Illness for Verywell Health

This repository runs one YAML files in the .github/workflows directory: `iliRunner.yml`.

The YAML file runs on a cron schedule at 8pm UTC every day that will run the Python script `fluLikeIllness.py` which takes the latest CDC Influenza-Like Illness [JSON data](https://gis.cdc.gov/grasp/FluView1/Phase1IniP) from the CDC's [Weekly U.S. Influenza Surveillance Report](https://www.cdc.gov/flu/weekly/index.htm) and uses it to update the Datawrapper map that is present on Verywell health's [Flu by the Numbers article](https://www.verywellhealth.com/flu-cases-by-state-5202670).

The Python script also outputs a CSV file `latestILIData.csv` that is sent to the Datawrapper charts via the [Datawrapper API](https://developer.datawrapper.de/) and also commited to the repository.