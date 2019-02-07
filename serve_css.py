@app.get('/question/<number>')
def question(number):
    statement = questions[number].statement
    return template('index.html', question_number=number, question=statement)
    return template('index.css', question_number=number, question=statement)
    return template('style.css', question_number=number, question=statement)
    
@app.get('/question/<path:path>')
