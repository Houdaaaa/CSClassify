This project displays a classification of computer science domains and the link between the computer science buzz words and the classification.

To use it:

1. Install the necessary dependencies
The file "requirements.txt" contains all the necessary dependencies and their versions.
It is recommended to create a virtual environment (pycharm does it automatically) in which all these dependencies must be installed using the "pip" command.

2. Creating a Neo4j database
First of all, you must install Neo4j (Neo4j Desktop is recommended) and create a new project called EDITx.
The password defined must be "editx".
To start the server, click on "start".

3. Setting up the classification
The database_creation() function in the "models.py" file allows to create all the classification and all the necessary links between fields and with buzz words (thanks to jsons files).
It is therefore sufficient to launch this function only once to fill the database.

4. Starting the project
It is possible to launch the application using the following command:
                        Python run.py
On condition that you are in the directory where the file "run.py" is located.
If you use an IDE like Pycharm, launch the project using the "run" button.
A local link will then be presented to you to discover the application.

5. Modification of the classification
For the moment, the classification modification is done via jsons files.
Once the modification is complete, launch the "delete_all" function to empty the entire database.
Then launch the "database_creation" function to rebuild the database.
This is of course an interim solution, improvements will be made during the TFE.
