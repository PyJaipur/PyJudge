@app.get('/css/<path:path>')
def download(path):
    return static_file(path, root=PyJudge)      
