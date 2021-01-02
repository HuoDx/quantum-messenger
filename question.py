from typing import List
import time
import datetime
from uuid import uuid4

class Question:
    def __init__(self, uid, question, asker, answerer,
                 answer = None, ask_time = None, answer_time = None):
        self.uid = uid
        self.question = question
        self.answer = answer
        self.asker = asker
        self.answerer = answerer
        self.ask_time = ask_time
        self.answer_time = answer_time
    
    @classmethod
    def ask(cls, question, asker_uid, answerer_uid):
        '''
        generates a question from an ask.
        *notice this method will NOT update the question in the database system.*
        '''
        return Question(
            str(uuid4()),
            question,
            asker_uid,
            answerer_uid,
        )
    def has_answered(self):
        return (self.answerer is not None and self.answer_time is not None and self.answer is not None and self.answer != '')
    
    # Don't ever write anyting like this - it's a total mess
    # But I'm hurry to finish and meet my girlfriend online so it's fine ;)
    convert_timestamp = lambda x: datetime.datetime.strftime(datetime.datetime.fromtimestamp(x), '%b %d, %Y %H:%M:%S')
    
    def __str__(self):
        ans = ''
        ans+=('Question:')
        ans+=('  · UID: %s\n\n'%self.uid)
        
        ans+=('  · Question: %s\n'%self.question)
        ans+=('    · Asker: %s\n'%self.asker)
        ans+=('    · Ask Time: %s\n\n'%Question.convert_timestamp(self.ask_time if self.ask_time is not None else time.time()))
        
        if self.has_answered():
            ans+=('  · Answer: %s\n'%self.answer)
            ans+=('    · Answerer: %s\n'%self.answerer)       
            ans+=('    · Answer Time: %s\n\n'%Question.convert_timestamp(self.answer_time))
        
        return ans
questions = {} # question_uid -> Question
asker_questions = {} # asker_uid -> list<Question>
answerer_questions = {} # answerer_uid -> list<Question>

def add_question(question_object: Question):
    global questions, asker_questions, answerer_questions
    
    # update the timestamp
    question_object.ask_time = time.time()
    
    questions.update({question_object.uid: question_object})
    
    if question_object.asker is None or question_object.answerer is None:
        raise Exception('Incomplete question.')
    
    if question_object.asker in asker_questions:
        asker_questions.get(question_object.asker).append(question_object.uid)
    else:
        asker_questions.update({question_object.asker: question_object.uid})
    
    if question_object.answerer in answerer_questions:
        answerer_questions.get(question_object.answerer).append(question_object.uid)
    else:
        answerer_questions.update({question_object.answerer: question_object.uid})
        
    return True

def get_questions_by_asker(asker_uid) -> List[Question]:
    global questions, asker_questions
    ans = []
    for question_uid in asker_questions.get(asker_uid,[]):
        ans.append(questions.get(question_uid))
    return ans

def get_questions_by_answerer(answerer_uid) -> List[Question]:
    global questions, answerer_questions
    ans = []
    for question_uid in answerer_questions.get(answerer_uid,[]):
        ans.append(questions.get(question_uid))
    return ans

def answer_question(question_uid, answer, answerer_uid):
    global questions, answerer_questions
    if question_uid not in answerer_questions.get(answerer_uid,[]):
        err_msg = 'The answerer %s is attempting to answer a question that is not belong to himself; rejected.'%answerer_uid
        raise Exception(err_msg)
        return False, err_msg
    question:Question = questions.get(question_uid)
    if question.answerer != answerer_uid:
        err_msg = 'The answerer %s is attempting to answer a question that is not belong to himself; rejected.'%answerer_uid
        raise Exception(err_msg)
        return False, err_msg
    question.answer = answer
    question.answer_time = time.time()
    return True

# test
# import uuid
# print('Test: building ')
    
# askr = str(uuid4())
# ansr =str(uuid4())
# q = Question.ask('你好，世界？', askr, ansr)
# print(q)
# add_question(q)
# print( q)
# answer_question(q.uid, '你好。', ansr)
# print(q)


            