Using the setup script
1.1	Extract the zip file into a directory, or
1.2	Open up a terminal and clone the repository:
	git clone https://github.com/unsw-cse-comp3900-9900-21T3/capstone-project-3900-h10a-awae.git
2.	Open the project directory and run the setup shell script:
	bash setup.sh
3.	Open a browser and type in the url: 127.0.0.1:5002


Manual install
If the setup script does not work, follow the manual install instructions.
1.1	Extract the zip file into a directory, or
1.2	Open up a terminal and clone the repository:
	git clone https://github.com/unsw-cse-comp3900-9900-21T3/capstone-project-3900-h10a-awae.git
2.	Open project directory and setup the virtual environment in your directory:
	python3 -m venv venv
3.	Activate the virtual environment:
	Windows: ./venv/Scripts/activate
	Linux: source ./venv/bin/activate
4.	Install the python requirements:
	pip3 install -r requirements.txt
5.	Go to the flask directory in the project folder:
	cd flask_project
6.	Run the flask server in the terminal:
	python3 run.py --no-livereload


Please refer to section 2 of our report to learn how to use our website's functionalities.