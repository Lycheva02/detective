# detective
Detective game using telebot

!!!You should run parsers from root directory!!!
For example:
python parsing\parser.py templates\test.txt

- parsing
 contains scripts for parsing the stories and adding them to the DB
  - parser.py
  parses the scenario story/locations/characters
  -question_parser.py
  parses the questions file (NEEDS SCENARIO ID AS argv[1])

- templates
file formats templates
  - test.txt
  template of file with the story
  - question_test.txt
  template of file with the questions