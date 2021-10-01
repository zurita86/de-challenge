# Data Engineer - Challenge

## Deployment Steps

This ETL process works on Google Cloud with Cloud Storage and Cloud Functions. Please follow the steps into a Google Cloud. For this, you could use a GCP SDK (if you had installed), Cloud Shell or a GCP User Interface.

1. Create a project before the deployment.
    -- Go to: https://console.cloud.google.com/
    -- Open a Cloud Shell on the top right corner icon.
    -- Run the next command. (You could change the id and name of the project for whatever you want)
        -- gcloud projects create de-challenge-1 --name="DE Challenge"
    -- Authorize Cloud Shell Pop Up. Then click "Authorize" blue button.
    -- Open the new Project and Enable Billing using the displayed top alert. By the click of "Enable Billing" link.
    -- Open Cloud Storage
        -- https://console.cloud.google.com/storage/
    -- Open a new Cloud Shell
    -- Enable the APIs we go to use. Use the next commands
        -- gcloud services enable dataproc.googleapis.com 
        -- gcloud services enable cloudbuild.googleapis.com
    -- Create a Bucket with the next command. (You could change the region and name of the bucket for whatever you want)
        -- gsutil mb -c standard -l us-central1 gs://javiers-de-challenge-bucket
    -- Open the bucket in the User Interface.
    -- Use the option for the "Upload Folder" and upload queries folder and then the pipeline folder.
    -- Now we need to create a Cloud Function from the UI.
        -- https://console.cloud.google.com/functions/
        -- Details of function
            -- Name: (whatever you want)
            -- Region: The same you choose when you create a bucket. For example. us-central1
            -- Trigger type: Cloud Storage
            -- Event Type: Finalize/Create
            -- Bucket: Choose the previous bucket created. For example. javiers-de-challenge-bucket
                -- Click Save
            -- Expand "Runtime, build, connections and security settings" options.
                -- Into Runtime Tab Change only the next two values:
                    -- Memory Allocated: 1 GB
                    -- Timeout: 300 seconds
            -- Click Next and continue editing cloud function parameters.
            -- Select Runtime: Python 3.7
            -- Change "Entry point" for: trigger_spark_job
            -- Select main.py from left side and replace the code with the code into the folder function-source/main.py
                --- IMPORTANT: CHANGE THE PARAMETERS INTO THE LINES 13 TO 16 WITH YOUR OWN CONFIGURATION. FOR EXAMPLE.
                    -- project = 'de-challenge-1'
                    -- cluster_name = 'cluster-tmp-01'
                    -- region = 'us-central1'
                    -- zone = 'us-central1-a'
            -- Select requirements.txt from left side and replace the code with the code into the folder function-source/requirements.txt
            -- Click "Deploy" button below.
    -- Go back to Cloud Storage.
        -- https://console.cloud.google.com/storage/
    -- Open the previous created bucket.
    -- We are ready to test the pipeline.
        -- Use the option for the "Upload Folder" and upload data folder.

    Pipeline process
    ------

    At this time a new Dataproc cluster must be in the process of being created. And you can see at: https://console.cloud.google.com/dataproc/clusters
    When the cluster is created you can see into the Jobs menu one job per queries exists in queries folder. The jobs get done about 1min before start.
    When the process is donde you could see a new folder into the bucket with name "output". Into this folder you could find the files generates by the pipeline separeted into a folders.
    Important Notes: 
        -- The process create a patch for a day run. If you run more than one time in the same day the pipeline replace the previous results. But if you run in another day, you can find a new folder for a day.
        -- The process create a cluster with a deletion rule after 30min of idle. But if you need to run a new pipeline and the cluster still be alive, you first need to delete them.
        -- The process only be executed when someone upload a new result.csv file into a data folder inside the bucket.

    Other Notes:
    
    I think a lot of better ways to solve the problem, but for the challenge I think as easy as posible, because we could use a GCloud Composer for Scheduled and automatic trigger day by day, but the result.csv file come from Kaggle platform and to do a download is needed a credentials.

    Thinking in the data scientist the pipeline allow to add or modify the queries they could need to evaluate the same data in a diferent way. To test this function you only had to create a new query .sql into a queries folder. But with more queries, more performace you need to configure into a Cloud Function and Dataproc Cluster parameters.

    In the same way, if you see the queries I add, one with a where based on date, to evaluate only the 2018 games.

    And the other hand I think a lot how to rank the games if I have two diferent scores, the metascore and the users score. Then I think that I could evaluate both after normalization, because of that users score is multiply by 10 and I set a weigth for each score, assigning 75% to metascore and 25% to users score. With this, I create a new column named custom_score.

    All of this parameter could easily change by the data scientist needs.

    The pipeline could have as an output a Bigquery Table for example. But for this challenge I decide to only export in a CSV to avoid more complex deployment process.

    Data Model
    -------
    For the Data Model I used Moon Modeler App on Mac OSX because basically I dont have any other installed and there no free options for Mac. Because of that I use a Trial period of this App.





    
    

    
