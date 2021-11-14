from server import app

def chunk(n, l):
    n = max(1, n)
    return [l[i:i+n] for i in range(0, len(l), n)]

@app.context_processor
def inject_utility_funcs():
    return dict(chunk=chunk)

app.jinja_env.globals['chunk'] = chunk