# CS 410 Quiz App
This is an application designed for UIUC CS410 students to quiz themselves on weekly problems. User's have the ability to take a specific quiz, search for desired questions within a quiz, or use topic mining to generate possible sub quizzes. 

## Getting Started
First install needed dependencies (assumes you have both python3 and pip installed):
```bash
# Ensure your pip is up to date
pip install --upgrade pip

# install metapy
pip install metapy

# install Unofficial Client for Piazza's Internal API
pip install piazza-api
```
You can now download or clone the repository.

## Usage
Open a terminal and navigate to the files. Enter this command to run the application:
```bash
python main.py
```

## Description of Files
*See function docstrings in py files for detailed descriptions*

### Constants.py
Contains constants used in the program.

### DBManager.py
Handles all database interactions for the program using sqlite. 
The database is used to store/retrieve user's piazza credentials, quizzes, and all quiz questions. 
  
### PiazzaQuestions.py
Wrapper for the unofficial piazza API. Used to login the user, check for new quizzes on piazza, 
and prepare the piazza post to be stored in the database.  
  
### Quiz.py
Represents what a quiz is. Handles the actual quizzing process 
and can mark questions so the user can quiz themselves on specific questions later.
  
### main.py
This is the 'executable' of the application. 
Creates the interactive environment in the terminal for the user to login and navigate through menu options. 
Provides the user with the ability to take quizzes, search for certain quiz terms, and perform topic mining. 

### config.toml
Used by metapy for searching and topic mining.
  
### stopwords.txt
Contains a list of words that metapy will ignore during searching and topic mining.
  
## Important
At the time of this writing, piazza weekly quiz post were titled 'Week# submitted quiz questions' - where # is a number. 
Questions also had to follow the following format:
  #CorrectAnswer# Question starts here..... : (A) ..., (B), ... (C) ,...
  ex) #B# Which of the following is true? (A) answer1, (B) answer2
If these conventions change, the parse_question function and is_quiz_post function in PiazzaQuestions.py will need to be updated.
