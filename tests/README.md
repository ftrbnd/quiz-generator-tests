# User Stories

[Google Sheets reference](https://docs.google.com/spreadsheets/d/1eWsab3ukhgWHyLVQjxm6Ly8NB9e8q8ZRKWfG-8ySWR4/edit?usp=sharing)

## Preprocessing

| ID  | User Story                                                                                                                                             | Implementation                                                   |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| 2   | As a student, I want to upload my notes so that I can be quizzed on the subject matter                                                                 | [input_test.py](preprocessing/input_test.py)                     |
| 12  | As an instructor, I want to be able to specify the question types so that students demonstrate their knowledge in different ways                       | [questtype_test.py](preprocessing/questtype_test.py)                     |
| 13  | As a student, I want to set the difficulty level so that I can slowly improve my knowledge                                                             | [test_story_13.py](preprocessing/test_story_13.py)               |
| 16  | As a professor, I want to upload my materials in whatever file format I have (PDF, text, images) so that the system can create quizzes from any source | [file_upload_test.py](preprocessing/file_upload_test.py)         |
| 65  | As a student, I want the system to automatically clean and structure my uploaded content so that irrelevant text doesn't interfere with the generation | [clean_stopwords_test.py](preprocessing/clean_stopwords_test.py) |

## Creating Questions

| ID  | User Story                                                                                                                 | Implementation                                                     |
| --- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 9   | As a student, I want the system to detect how many times a single word appears in my file                                  | [analysis_test.py](question_creation/analysis_test.py)             |
| 10  | As a student, I want the system to recognize the importance of a word mentioned across the files I upload                  | [analysis_test.py](question_creation/analysis_test.py)             |
| 11  | As a researcher, I want to upload a document to be tested on the source material                                           | [file_upload_test.py](preprocessing/file_upload_test.py)           |
| 22  | As a user, I want to create question pools so that different students receive different questions covering the same topics | [test_question_pools.py](question_creation/test_question_pools.py) |
| 43  | As an instructor, I want to tag questions by topic or standard so that I can analyze performance by curriculum area        | [test_question_tags.py](question_creation/test_question_tags.py)   |

## Quiz Generation

| ID  | User Story                                                                                                           | Implementation                                               |
| --- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| 1   | As a teacher, I want to specify the number of questions so that my quiz fits my lesson plan                          | [input_test.py](preprocessing/input_test.py)                 |
| 21  | As an educator, I want to randomize question order so that each student receives a different sequence                | [shuffle_quiz_test.py](quiz_generation/shuffle_quiz_test.py) |
| 44  | As a student, I want to receive explanations for the answers so that I can better understand the material            | [explanations_test.py](quiz_generation/explanations_test.py) |
| 57  | As a student, I want to download quizzes for offline completion so that I can study without internet access          | [download_test.py](quiz_generation/download_test.py)         |
| 60  | As an instructor, I want to shuffle answer choices independently of question order so that memorization is minimized | [test_story_60.py](quiz_generation/test_story_60.py)         |
| 63  | As a teacher, I want the system to output the quiz in a txt/csv file                                                 | [download_test.py](quiz_generation/download_test.py)         |
