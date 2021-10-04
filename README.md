# Database code
Branch managed by Arthur Sze (z5165205)
## Files
- data: sample data in csv format
- db: database
- create_db.py: code to initialise Mongo database with sample data
- db.sh: start up database

## Python and MongoDB Setup
1. Have Python 3.6 or greater and pip3 installed.
2. Create a python virtual environment and activate it (in command prompt, vscode, etc); from now on everything is done inside the virtual environment.
3. Navigate to requirements file and type ```pip install -r requirements.txt```
4. The Mongo database needs to be setup and run locally. Installation instructions for mongodb [Windows](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/).
5. Run the shell script, this will open up a bash window run the mongoDB server. If necessary, [add mongo to PATH]. (https://dangphongvanthanh.wordpress.com/2017/06/12/add-mongos-bin-folder-to-the-path-environment-variable/)
6. Run ```python create_db.py```
7. To shut down the DB, ctrl+c or exit the bash window.


